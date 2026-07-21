from odoo import fields, models


class PharmacieOrdonnance(models.Model):
    _name = 'pharmacie.ordonnance'
    _description = "Ordonnance médicale"
    _order = 'date_ordonnance desc'

    patient_id = fields.Many2one('res.partner', string="Patient")
    medecin = fields.Char(string="Médecin prescripteur")
    structure = fields.Char(string="Structure médicale")
    date_ordonnance = fields.Date(string="Date de l'ordonnance")
    state = fields.Selection(
        [
            ('brouillon', "Brouillon"),
            ('validee', "Validée"),
            ('delivree', "Délivrée"),
            ('annulee', "Annulée"),
        ],
        string="Statut", default='brouillon')
    scan_ordonnance = fields.Binary(string="Scan de l'ordonnance")

    # posologie_ids sera ajouté lorsque pharmacie.posologie existera (ticket #17).
    # vente_id sera ajouté lorsque pharmacie.vente existera (tickets #20/#19).
