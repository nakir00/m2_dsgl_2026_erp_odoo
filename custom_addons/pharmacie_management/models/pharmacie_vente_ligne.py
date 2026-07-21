from odoo import fields, models


class PharmacieVenteLigne(models.Model):
    _name = 'pharmacie.vente.ligne'
    _description = "Ligne de vente"

    vente_id = fields.Many2one(
        'pharmacie.vente', string="Vente", required=True, ondelete='cascade', index=True)
    medicament_id = fields.Many2one(
        'pharmacie.medicament', string="Médicament", required=True,
        ondelete='restrict', index=True)
    quantite = fields.Float(string="Quantité", default=1.0)

    currency_id = fields.Many2one(
        'res.currency', string="Devise",
        default=lambda self: self.env.company.currency_id)
    prix_unitaire = fields.Monetary(string="Prix unitaire")

    # lot_id sera ajouté au ticket #23 (décrémentation des lots à la confirmation).
