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

    prix_unitaire = fields.Float(string="Prix unitaire (FCFA)")
    montant_ht = fields.Float(
        string="Montant HT", compute='_compute_montants', store=True)
    montant_tva = fields.Float(
        string="Montant TVA", compute='_compute_montants', store=True)
    montant_ttc = fields.Float(
        string="Montant TTC", compute='_compute_montants', store=True)
    lot_id = fields.Many2one(
        'pharmacie.lot', string="Lot", readonly=True,
        help="Lot consommé (FEFO) pour cette ligne à la confirmation de la vente.")

    @api.depends('quantite', 'prix_unitaire', 'medicament_id.taux_tva')
    def _compute_montants(self):
        for line in self:
            line.montant_ht = line.quantite * line.prix_unitaire
            taux = float(line.medicament_id.taux_tva or 0)
            line.montant_tva = line.montant_ht * taux / 100
            line.montant_ttc = line.montant_ht + line.montant_tva
