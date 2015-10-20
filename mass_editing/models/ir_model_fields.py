# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C):
#        2012-Today Serpent Consulting Services (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import models, api


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    @api.model
    def search(self, args, offset=0, limit=1, order=None, count=False):
        model_domain = []
        operator_blacklist = ['ilike']
        for domain in args:
            # TODO Functionality breaks when searching with ilike
            if (len(domain) > 2 and domain[0] == 'model_id' and
                    isinstance(domain[2], basestring) and
                    domain[1] not in operator_blacklist):
                model_domain += [('model_id', 'in', map(
                    int, domain[2][1:-1].split(',')))]
            else:
                model_domain.append(domain)
        return super(IrModelFields, self).search(
            model_domain, offset=offset, limit=limit, order=order, count=count)
