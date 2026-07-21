from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PharmacieVente(models.Model):
    _name = 'pharmacie.vente'
    _description = "Vente au comptoir"
    _order = 'date_vente desc'

    reference = fields.Char(string="Référence", readonly=True, copy=False)
    client_id = fields.Many2one('res.partner', string="Client")
    vendeur_id = fields.Many2one(
        'res.users', string="Vendeur", default=lambda self: self.env.user)
    ordonnance_id = fields.Many2one('pharmacie.ordonnance', string="Ordonnance")
    state = fields.Selection(
        [
            ('brouillon', "Brouillon"),
            ('confirmee', "Confirmée"),
            ('annulee', "Annulée"),
        ],
        string="Statut", default='brouillon')
    paiement = fields.Selection(
        [
            ('especes', "Espèces"),
            ('carte', "Carte bancaire"),
            ('mobile_money', "Mobile Money"),
            ('autre', "Autre"),
        ],
        string="Mode de paiement")
    date_vente = fields.Datetime(string="Date de vente", default=fields.Datetime.now)
    note = fields.Text(string="Note")
    ligne_ids = fields.One2many(
        'pharmacie.vente.ligne', 'vente_id', string="Lignes de vente")

    currency_id = fields.Many2one(
        'res.currency', string="Devise",
        default=lambda self: self.env.company.currency_id)
    montant_ht = fields.Monetary(
        string="Montant HT", compute='_compute_montants', store=True)
    montant_tva = fields.Monetary(
        string="Montant TVA", compute='_compute_montants', store=True)
    montant_ttc = fields.Monetary(
        string="Montant TTC", compute='_compute_montants', store=True)

    @api.depends('ligne_ids.montant_ht', 'ligne_ids.montant_tva', 'ligne_ids.montant_ttc')
    def _compute_montants(self):
        for vente in self:
            vente.montant_ht = sum(vente.ligne_ids.mapped('montant_ht'))
            vente.montant_tva = sum(vente.ligne_ids.mapped('montant_tva'))
            vente.montant_ttc = sum(vente.ligne_ids.mapped('montant_ttc'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('pharmacie.vente')
        return super().create(vals_list)

    def write(self, vals):
        result = super().write(vals)
        if vals.get('state') == 'confirmee':
            for vente in self:
                if vente.ordonnance_id:
                    vente.ordonnance_id.state = 'delivree'
        return result

    def _check_ordonnance_requise(self):
        self.ensure_one()
        medicaments_sur_ordonnance = self.ligne_ids.medicament_id.filtered('sur_ordonnance')
        if medicaments_sur_ordonnance and not self.ordonnance_id:
            raise UserError(_(
                "Une ordonnance est requise pour vendre : %s."
            ) % ', '.join(medicaments_sur_ordonnance.mapped('name')))

    def action_confirmer(self):
        for vente in self:
            if vente.state != 'brouillon':
                continue
            vente._check_ordonnance_requise()
            for line in vente.ligne_ids:
                lot = self.env['pharmacie.lot'].search([
                    ('medicament_id', '=', line.medicament_id.id),
                    ('state', '=', 'valide'),
                    ('quantite_actuelle', '>=', line.quantite),
                ], order='date_peremption asc', limit=1)
                if not lot:
                    raise UserError(_(
                        "Stock insuffisant pour %(medicament)s : aucun lot disponible ne "
                        "couvre la quantité demandée (%(demande).2f)."
                    ) % {
                        'medicament': line.medicament_id.name,
                        'demande': line.quantite,
                    })
                lot.quantite_actuelle -= line.quantite
                line.lot_id = lot.id
            vente.state = 'confirmee'

    def action_annuler(self):
        for vente in self:
            if vente.state == 'annulee':
                continue
            if vente.state == 'confirmee':
                for line in vente.ligne_ids:
                    if line.lot_id:
                        line.lot_id.quantite_actuelle += line.quantite
            vente.state = 'annulee'
