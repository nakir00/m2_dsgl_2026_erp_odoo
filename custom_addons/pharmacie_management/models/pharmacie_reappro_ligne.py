from odoo import api, fields, models


class PharmacieReapproLigne(models.Model):
    _name = 'pharmacie.reappro.ligne'
    _description = "Ligne de réapprovisionnement"

    reappro_id = fields.Many2one(
        'pharmacie.reappro', string="Réapprovisionnement",
        required=True, ondelete='cascade', index=True)
    medicament_id = fields.Many2one(
        'pharmacie.medicament', string="Médicament", required=True,
        ondelete='restrict', index=True)
    quantite = fields.Float(string="Quantité", default=1.0)

    currency_id = fields.Many2one(
        'res.currency', string="Devise",
        default=lambda self: self.env.company.currency_id)
    prix_unitaire = fields.Monetary(string="Prix unitaire")
    montant = fields.Monetary(
        string="Montant", compute='_compute_montant', store=True)

    @api.depends('quantite', 'prix_unitaire')
    def _compute_montant(self):
        for line in self:
            line.montant = line.quantite * line.prix_unitaire
