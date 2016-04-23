# -*- coding: utf-8 -*-

from openerp import models, fields

# CIIU, ICA y CREE


class CiiuIcaCree(models.Model):
    _name = "lista.ciiu_ica_cree"
    _description = "Lista CIIU, ICA y CREE"

    codigo = fields.Char('Código', size=20, required=True)
    name = fields.Char('Descripción', size=20, required=True)
    parent = fields.Char('Padre', size=20, required=True)
    type = fields.Char('Tipo', size=20, required=True)

