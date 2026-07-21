from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PharmacieLot(models.Model):
    _name = 'pharmacie.lot'
    _description = "Lot de stock d'un médicament"
    _order = 'date_peremption'

    numero_lot = fields.Char(string="Numéro de lot", readonly=True, copy=False)
    medicament_id = fields.Many2one(
        'pharmacie.medicament', string="Médicament",
        required=True, ondelete='restrict', index=True)
    date_fabrication = fields.Date(string="Date de fabrication")
    date_reception = fields.Date(string="Date de réception")
    date_peremption = fields.Date(string="Date de péremption")
    quantite_initiale = fields.Float(string="Quantité initiale")
    quantite_actuelle = fields.Float(string="Quantité actuelle")

    currency_id = fields.Many2one(
        'res.currency', string="Devise",
        default=lambda self: self.env.company.currency_id)
    prix_achat_unitaire = fields.Monetary(string="Prix d'achat unitaire")
    jours_avant_peremption = fields.Integer(
        string="Jours avant péremption", compute='_compute_jours_avant_peremption')

    # reappro_id sera ajouté lorsque pharmacie.reappro existera (ticket #26).

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('numero_lot'):
                vals['numero_lot'] = self.env['ir.sequence'].next_by_code('pharmacie.lot')
        return super().create(vals_list)

    @api.constrains('date_fabrication', 'date_peremption')
    def _check_dates_lot(self):
        for rec in self:
            if (rec.date_fabrication and rec.date_peremption
                    and rec.date_peremption <= rec.date_fabrication):
                raise ValidationError(
                    _("La date de péremption doit être postérieure à la date de fabrication."))

    @api.depends('date_peremption')
    def _compute_jours_avant_peremption(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.jours_avant_peremption = (
                (rec.date_peremption - today).days if rec.date_peremption else 0)
