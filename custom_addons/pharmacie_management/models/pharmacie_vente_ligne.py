from odoo import api, fields, models


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
    montant_ht = fields.Monetary(
        string="Montant HT", compute='_compute_montants', store=True)
    montant_tva = fields.Monetary(
        string="Montant TVA", compute='_compute_montants', store=True)
    montant_ttc = fields.Monetary(
        string="Montant TTC", compute='_compute_montants', store=True)
    lot_id = fields.Many2one(
        'pharmacie.lot', string="Lot", readonly=True,
        help="Lot consommé (FEFO) pour cette ligne à la confirmation de la vente.")

    @api.depends('quantite', 'prix_unitaire', 'medicament_id.tva')
    def _compute_montants(self):
        for line in self:
            line.montant_ht = line.quantite * line.prix_unitaire
            line.montant_tva = line.montant_ht * (line.medicament_id.tva or 0.0) / 100
            line.montant_ttc = line.montant_ht + line.montant_tva
