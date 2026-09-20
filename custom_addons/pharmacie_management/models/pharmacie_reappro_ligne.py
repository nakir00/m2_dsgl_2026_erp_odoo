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
    lot_ids = fields.One2many(
        'pharmacie.lot', 'reappro_ligne_id', string="Lots reçus")
    quantite_recue = fields.Float(
        string="Quantité reçue", compute='_compute_quantites_reception')
    quantite_restante_a_recevoir = fields.Float(
        string="Quantité restante à recevoir", compute='_compute_quantites_reception')

    prix_unitaire = fields.Float(string="Prix unitaire (FCFA)")
    montant = fields.Float(
        string="Montant", compute='_compute_montant', store=True)

    @api.depends('quantite', 'prix_unitaire')
    def _compute_montant(self):
        for line in self:
            line.montant = line.quantite * line.prix_unitaire

    @api.depends('quantite', 'lot_ids.quantite_initiale')
    def _compute_quantites_reception(self):
        for line in self:
            line.quantite_recue = sum(line.lot_ids.mapped('quantite_initiale'))
            line.quantite_restante_a_recevoir = max(
                line.quantite - line.quantite_recue, 0.0)
