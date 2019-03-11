import xlsxwriter

class ExcelWriter(object):

    def __init__(self):
        self.file_path = 'excel_export_2.xlsx'
        self.line_number = 0
        self.column_number = 0

    def write_output(self, output):

        workbook = xlsxwriter.Workbook(self.file_path)
        bold = workbook.add_format({'bold': True})
        self.column_number = 0
        self.line_number = 0

        # The first for is for each portal type.  Sample, Client, project etc ...
        # print('----output data-----')
        # print(output)
        for key, output_data in output.iteritems():
            work_sheet = workbook.add_worksheet(key)

            # Second For for example is each sample in samples etc etc ...
            headings = output_data[0]
            data = output_data[1]

            self.write_headings(work_sheet, headings, bold)
            self.write_data(work_sheet, data, headings)

        workbook.close()

    def write_headings(self, work_sheet, headings, bold):

        for heading in headings:
            work_sheet.write(self.line_number, self.column_number, heading, bold)
            self.column_number += 1

        self.line_number += 1
        self.column_number = 0

    def write_data(self, work_sheet, data, headings):
        # print('+=========')

        for datum in data:
            self.line_number += 1
            self.column_number = 0
            for heading in headings:
                # print('Printed data: %s: %s' %(heading, datum[heading]))
                work_sheet.write(self.line_number, self.column_number, str(datum[heading]))
                self.column_number += 1

        self.line_number = 0
        self.column_number = 0








# #
# workbook = xlsxwriter.Workbook('xlsx_demo_1.xlsx')
# worksheet = workbook.add_worksheet()
#
# worksheet.set_column('A:A', 20)
# bold = workbook.add_format({'bold': True})
#
# worksheet.write('A1', 'Hello')
# worksheet.write('A2', 'World', bold)
#
# worksheet.write(2, 0, 123)
# worksheet.write(3, 0, 123.456)
#
# workbook.close()





