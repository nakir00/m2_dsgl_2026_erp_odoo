from odoo import fields, models


class PharmacieOrdonnance(models.Model):
    _name = 'pharmacie.ordonnance'
    _description = "Ordonnance médicale"
    _order = 'date_prescription desc'

    patient_nom = fields.Char(string="Nom du patient")
    patient_age = fields.Integer(string="Âge du patient")
    patient_genre = fields.Selection(
        [('m', "Masculin"), ('f', "Féminin")], string="Genre du patient")
    medecin_nom = fields.Char(string="Médecin prescripteur")
    structure_sante = fields.Char(string="Structure de santé")
    date_prescription = fields.Date(string="Date de prescription")
    medicament_ids = fields.Many2many(
        'pharmacie.medicament', string="Médicaments prescrits")
    posologie_ids = fields.One2many(
        'pharmacie.posologie', 'ordonnance_id', string="Détail posologique")
    statut = fields.Selection(
        [
            ('en_attente', "En attente"),
            ('delivree_partiellement', "Délivrée partiellement"),
            ('delivree_complete', "Délivrée complètement"),
        ],
        string="Statut", default='en_attente')
    vente_id = fields.Many2one('pharmacie.vente', string="Vente associée")
    scan_ordonnance = fields.Binary(string="Scan de l'ordonnance")
    scan_ordonnance_filename = fields.Char(string="Nom du fichier scanné")
