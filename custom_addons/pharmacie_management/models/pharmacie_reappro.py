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

    # ligne_ids sera ajouté au ticket #27.
    # montant_total sera ajouté au ticket #28.

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('pharmacie.reappro')
        return super().create(vals_list)
