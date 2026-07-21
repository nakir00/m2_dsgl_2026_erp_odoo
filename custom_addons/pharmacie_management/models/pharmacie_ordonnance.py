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
    scan_ordonnance_filename = fields.Char(string="Nom du fichier scanné")
    posologie_ids = fields.One2many(
        'pharmacie.posologie', 'ordonnance_id', string="Médicaments prescrits")
    vente_ids = fields.One2many(
        'pharmacie.vente', 'ordonnance_id', string="Ventes")
