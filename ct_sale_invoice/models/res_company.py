# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class RESCompany(models.Model):
    _inherit = "res.company"

    sltech_footer = fields.Char('Footer')
    sltech_header1 = fields.Char('Header 1st Line')
    sltech_header2 = fields.Char('Header 2nd Line')
    sltech_header3 = fields.Char('Header 3rd Line')
    sltech_header4 = fields.Char('Header 4th Line')