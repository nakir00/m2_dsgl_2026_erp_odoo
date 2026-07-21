from odoo import Command, api, fields, models


class PharmacieBilanCaisseWizard(models.TransientModel):
    _name = 'pharmacie.bilan.caisse.wizard'
    _description = "Bilan de caisse"

    date_debut = fields.Date(
        string="Date de début", required=True, default=fields.Date.context_today)
    date_fin = fields.Date(
        string="Date de fin", required=True, default=fields.Date.context_today)

    ca_total = fields.Float(
        string="Chiffre d'affaires total", compute='_compute_bilan')
    nombre_ventes = fields.Integer(
        string="Nombre de ventes", compute='_compute_bilan')
    panier_moyen = fields.Float(
        string="Panier moyen", compute='_compute_bilan')
    ligne_vendeur_ids = fields.One2many(
        'pharmacie.bilan.caisse.wizard.ligne', 'wizard_id',
        string="Chiffre d'affaires par vendeur", compute='_compute_bilan', store=True)

    @api.depends('date_debut', 'date_fin')
    def _compute_bilan(self):
        Vente = self.env['pharmacie.vente']
        for wizard in self:
            ventes = Vente.browse()
            if wizard.date_debut and wizard.date_fin:
                ventes = Vente.search([
                    ('statut', '=', 'confirmee'),
                    ('date_vente', '>=', wizard.date_debut),
                    ('date_vente', '<=', wizard.date_fin),
                ])
            wizard.ca_total = sum(ventes.mapped('montant_ttc'))
            wizard.nombre_ventes = len(ventes)
            wizard.panier_moyen = (
                wizard.ca_total / wizard.nombre_ventes if wizard.nombre_ventes else 0.0)
            wizard.ligne_vendeur_ids = [
                Command.create({
                    'vendeur_id': vendeur.id,
                    'ca': sum(ventes.filtered(lambda v: v.vendeur_id == vendeur)
                              .mapped('montant_ttc')),
                    'nombre_ventes': len(ventes.filtered(lambda v: v.vendeur_id == vendeur)),
                })
                for vendeur in ventes.vendeur_id
            ]

    def action_imprimer(self):
        self.ensure_one()
        return self.env.ref('pharmacie_management.action_report_bilan_caisse').report_action(self)


class PharmacieBilanCaisseWizardLigne(models.TransientModel):
    _name = 'pharmacie.bilan.caisse.wizard.ligne'
    _description = "Chiffre d'affaires par vendeur du bilan de caisse"

    wizard_id = fields.Many2one(
        'pharmacie.bilan.caisse.wizard', required=True, ondelete='cascade')
    vendeur_id = fields.Many2one('res.users', string="Vendeur")
    ca = fields.Float(string="Chiffre d'affaires")
    nombre_ventes = fields.Integer(string="Nombre de ventes")
