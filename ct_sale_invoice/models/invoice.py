# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Invoice(models.Model):
    _inherit = 'account.invoice'

    delivery_date = fields.Date('Delivery Date')

    def get_total_discount(self):
        total_disc = 0
        for rec in self:
            for line in rec.invoice_line_ids:
                if line.fields_get(['discount_fixed']):
                    total_disc += line.discount_fixed
                else:
                    total_disc += (((line.discount * line.price_unit) * line.quantity) / 100)
        return total_disc + self.global_order_discount

    def get_extra_rows(self, invoice):
        if len(invoice.invoice_line_ids)<7:
            return (7-len(invoice.invoice_line_ids))*[1]
        return []

    def get_amount_untaxed(self):
        total_disc = self.get_total_discount()
        amount_after_discount = 0
        amount_after_discount = self.amount_untaxed - total_disc
        return amount_after_discount

    def address(self, company=False):
        partner_address = []
        for record in self:
            if record.partner_id.street:
                partner_address.append(record.partner_id.street)
            # if record.partner_id.city:
            # 	partner_address.append(record.partner_id.city)
            # if record.partner_id.country_id:
            # 	partner_address.append(record.partner_id.country_id.name)
            # if record.partner_id.zip:
            # 	partner_address.append(record.partner_id.zip)
            if company:
                partner_address = [record.company_id.street]
            partner_add = ','.join(str(e) for e in partner_address)
        return partner_add[:25]

    def get_qrcode_img(self):
        qrocde_id = self.env['qr.generator']

        data = ""
        if self.partner_id.name:
            data = str(self.company_id.name) + "\n"
        if self.company_id.vat:
            data += str(self.company_id.vat) + "\n"
        if self.date_invoice:
            data += str(self.date_invoice) + "\n"
        if self.amount_total:
            data += str(str(self.amount_total) + " " + str(self.company_id.currency_id.symbol)) + "\n"
        if self.amount_tax:
            data += str(str(self.amount_tax) + " " + str(self.company_id.currency_id.symbol)) + "\n"

        return qrocde_id.get_qr_code(data)
