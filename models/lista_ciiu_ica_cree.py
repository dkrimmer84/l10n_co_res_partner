# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

# CIIU, ICA y CREE


class CiiuIcaCree(osv.osv):
    _name = "lista.ciiu_ica_cree"
    _description = "Lista CIIU, ICA y CREE"

    _columns = {
        'codigo': fields.char('Código', size=20, required=True),
        'name': fields.char('Descripción', size=20, required=True),
        'parent': fields.char('Padre', size=20, required=True),
        'type': fields.char('Tipo', size=20, required=True),
    }
