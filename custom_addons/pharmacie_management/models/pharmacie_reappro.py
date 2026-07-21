from odoo import api, fields, models


class PharmacieReappro(models.Model):
    _name = 'pharmacie.reappro'
    _description = "Bon de commande fournisseur"
    _order = 'date_commande desc'

    reference = fields.Char(string="Référence", readonly=True, copy=False)
    fournisseur_id = fields.Many2one(
        'res.partner', string="Fournisseur", required=True,
        domain="[('is_fournisseur_pharma', '=', True)]")
    date_commande = fields.Date(string="Date de commande", default=fields.Date.context_today)
    date_reception_prevue = fields.Date(string="Date de réception prévue")
    state = fields.Selection(
        [
            ('brouillon', "Brouillon"),
            ('commandee', "Commandée"),
            ('recue_partiellement', "Reçue partiellement"),
            ('recue', "Reçue"),
        ],
        string="Statut", default='brouillon')
    note = fields.Text(string="Note")
    ligne_ids = fields.One2many(
        'pharmacie.reappro.ligne', 'reappro_id', string="Lignes")

    currency_id = fields.Many2one(
        'res.currency', string="Devise",
        default=lambda self: self.env.company.currency_id)
    montant_total = fields.Monetary(
        string="Montant total", compute='_compute_montant_total', store=True)

    @api.depends('ligne_ids.montant')
    def _compute_montant_total(self):
        for reappro in self:
            reappro.montant_total = sum(reappro.ligne_ids.mapped('montant'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('pharmacie.reappro')
        return super().create(vals_list)

    def action_receptionner(self):
        for reappro in self:
            if reappro.state == 'recue':
                continue
            for line in reappro.ligne_ids:
                self.env['pharmacie.lot'].create({
                    'medicament_id': line.medicament_id.id,
                    'quantite_initiale': line.quantite,
                    'quantite_actuelle': line.quantite,
                    'prix_achat_unitaire': line.prix_unitaire,
                    'date_reception': fields.Date.context_today(self),
                    'reappro_id': reappro.id,
                })
            reappro.state = 'recue'
