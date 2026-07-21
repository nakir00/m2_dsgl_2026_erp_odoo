from odoo import fields, models


class PharmaciePosologie(models.Model):
    _name = 'pharmacie.posologie'
    _description = "Posologie d'un médicament sur une ordonnance"

    ordonnance_id = fields.Many2one(
        'pharmacie.ordonnance', string="Ordonnance",
        required=True, ondelete='cascade', index=True)
    medicament_id = fields.Many2one(
        'pharmacie.medicament', string="Médicament",
        required=True, ondelete='restrict', index=True)
    instructions = fields.Text(string="Instructions de prise")
