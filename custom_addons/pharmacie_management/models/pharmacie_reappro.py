from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError


class PharmacieReappro(models.Model):
    _name = 'pharmacie.reappro'
    _description = "Bon de commande fournisseur"
    _order = 'date_commande desc'

    reference = fields.Char(string="Référence", readonly=True, copy=False)
    fournisseur_id = fields.Many2one(
        'res.partner', string="Fournisseur", required=True,
        domain="[('is_fournisseur_pharma', '=', True)]")
    date_commande = fields.Date(string="Date de commande", default=fields.Date.context_today)
    date_livraison_prevue = fields.Date(string="Date de livraison prévue")
    statut = fields.Selection(
        [
            ('brouillon', "Brouillon"),
            ('commandee', "Commandé"),
            ('recue_partiellement', "Reçu partiellement"),
            ('recue', "Reçu"),
        ],
        string="Statut", default='brouillon')
    note_interne = fields.Text(string="Note interne")
    ligne_ids = fields.One2many(
        'pharmacie.reappro.ligne', 'reappro_id', string="Lignes")
    lot_ids = fields.One2many(
        'pharmacie.lot', 'reappro_id', string="Lots reçus")

    montant_total = fields.Float(
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

    def action_commander(self):
        for reappro in self:
            if reappro.statut != 'brouillon':
                raise UserError(_(
                    "Seul un bon de commande en brouillon peut être commandé."))
            reappro.statut = 'commandee'

    def action_receptionner(self):
        self.ensure_one()
        if (not self.env.is_superuser()
                and not self.env.user.has_group(
                    'pharmacie_management.group_pharmacie_gestionnaire')):
            raise AccessError(_("Seul un gestionnaire peut valider une réception."))
        if self.statut not in ('commandee', 'recue_partiellement'):
            raise UserError(_(
                "Seule une commande passée (Commandé ou Reçu partiellement) "
                "peut être réceptionnée."))

        return {
            'type': 'ir.actions.act_window',
            'name': _("Réception fournisseur"),
            'res_model': 'pharmacie.reappro.reception.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': self._name,
                'active_id': self.id,
            },
        }
