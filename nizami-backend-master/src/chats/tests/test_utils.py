# from datetime import datetime

# import aspose.words as aw
# from django.test import SimpleTestCase

# from src.chats.utils import apply_inline_tracked_changes


# class ReplaceApplyInlineTrackedChanges(SimpleTestCase):
#     def setUp(self):
#         self.maxDiff = None

#     def test_single_run(self):
#         old_text = 'Hello World! yooo'
#         new_text = 'Hello there! yooo'
#         expected_tracking_text = 'Hello World! there! yooo\r'

#         doc = aw.Document()
#         para = aw.Paragraph(doc)
#         para.append_child(aw.Run(doc, old_text))

#         has_updates = apply_inline_tracked_changes(doc, para, new_text, 'jp', datetime.now())

#         self.assertTrue(has_updates)
#         self.assertEqual(expected_tracking_text, para.get_text())

#     def test_single_run_2(self):
#         old_text = 'The Sellers shall not be liable under the Warranties, in respect of any claim unless and until it shall receive from the Buyers a written notice of the claim (setting out details of the matters giving rise to any such claim under the Warranties or other claim in a manner enabling the Sellers to appreciate the nature and extent of such claim), in the case of a claim under the Warranties, on or before the expiry of Twelve (12) months period from the Completion'
#         new_text = 'The Sellers shall not be liable under the Warranties, in respect of any claim unless and until it receives from the Buyers a written notice of such claim (detailing the matters giving rise to the claim in a manner enabling the Sellers to fully understand its nature and extent), and in the case of a claim under the Warranties, such notice must be provided on or before the expiry of Eighteen (18) months from the Completion.'
#         expected_tracking_text = 'The Sellers shall not be liable under the Warranties, in respect of any claim unless and until it shall receive receives from the Buyers a written notice of the such claim (setting out details of (detailing the matters giving rise to any such claim under the Warranties or other claim in a manner enabling the Sellers to appreciate the fully understand its nature and extent of such claim), extent), and in the case of a claim under the Warranties, such notice must be provided on or before the expiry of Twelve (12) Eighteen (18) months period from the Completion Completion.\r'

#         doc = aw.Document()
#         para = aw.Paragraph(doc)
#         para.append_child(aw.Run(doc, old_text))

#         has_updates = apply_inline_tracked_changes(doc, para, new_text, 'jp', datetime.now())

#         self.assertTrue(has_updates)
#         self.assertEqual(expected_tracking_text, para.get_text())

#     def test_single_run_3(self):
#         old_text = '– Unresolved Matter. The Net Purchase Price, as detailed in Schedule 2, shall be allocated among the Sellers in the proportions set out in Schedule 2, reflecting each Seller’s pro rata portion of the Sale Shares being sold by such Seller.'
#         new_text = '– Unresolved Matter. For clarity, any adjustments arising from ‘Unresolved Matters’ shall be clearly explained in Schedule 2.'

#         expected_tracking_text = '– Unresolved Matter. The Net Purchase Price, as detailed For clarity, any adjustments arising from ‘Unresolved Matters’ shall be clearly explained in Schedule 2, shall be allocated among the Sellers in the proportions set out in Schedule 2, reflecting each Seller’s pro rata portion of the Sale Shares being sold by such Seller. 2.\r'

#         doc = aw.Document()
#         para = aw.Paragraph(doc)
#         para.append_child(aw.Run(doc, old_text))

#         has_updates = apply_inline_tracked_changes(doc, para, new_text, 'jp', datetime.now())

#         self.assertTrue(has_updates)
#         self.assertEqual(expected_tracking_text, para.get_text())

#     def test_single_run_4(self):
#         old_text = 'Subject to the terms and conditions of this Agreement, each Seller hereby agrees to sell and transfer to the Buyers, and the Buyers agrees to purchase (or procure the purchase by their nominees) from each Seller, the Sale Shares set opposite that Seller’s name in Schedule 1, free and clear of all Encumbrances, together with all rights attaching to those Sale Shares as at Completion (including the right to receive all dividends or distributions declared, made or paid on or after the 1st of April 2025).'
#         new_text = 'Subject to the terms and conditions of this Agreement, each Seller hereby agrees to sell and transfer to the Buyers, and the Buyers agree to purchase (or procure the purchase by their nominees) from each Seller, the Sale Shares set opposite that Seller’s name in Schedule 1, free and clear of all Encumbrances, together with all rights attaching thereto as of Completion (including the right to receive all dividends or distributions declared, made or paid on or after 1st April 2025).'

#         expected_tracking_text = 'Subject to the terms and conditions of this Agreement, each Seller hereby agrees to sell and transfer to the Buyers, and the Buyers agrees agree to purchase (or procure the purchase by their nominees) from each Seller, the Sale Shares set opposite that Seller’s name in Schedule 1, free and clear of all Encumbrances, together with all rights attaching to those Sale Shares thereto as at of Completion (including the right to receive all dividends or distributions declared, made or paid on or after the 1st of April 2025).\r'

#         doc = aw.Document()
#         para = aw.Paragraph(doc)
#         para.append_child(aw.Run(doc, old_text))

#         has_updates = apply_inline_tracked_changes(doc, para, new_text, 'jp', datetime.now())

#         self.assertTrue(has_updates)
#         self.assertEqual(expected_tracking_text, para.get_text())

#     def test_multi_runs(self):
#         new_text = 'Hello there! yooo'
#         expected_tracking_text = 'Hello World! there! yooo\r'

#         doc = aw.Document()
#         para = aw.Paragraph(doc)
#         para.append_child(aw.Run(doc, 'Hello '))
#         para.append_child(aw.Run(doc, 'World!'))
#         para.append_child(aw.Run(doc, ' yooo'))

#         has_updates = apply_inline_tracked_changes(doc, para, new_text, 'jp', datetime.now())

#         self.assertTrue(has_updates)
#         self.assertEqual(expected_tracking_text, para.get_text())

#     def test_multi_runs_2(self):
#         new_text = 'before the expiry of Eighteen (18) months'
#         expected_tracking_text = 'before the expiry of Twelve (12) Eighteen (18) months \r'

#         doc = aw.Document()
#         para = aw.Paragraph(doc)
#         para.append_child(aw.Run(doc, 'before the expiry of '))
#         para.append_child(aw.Run(doc, 'Twelve '))
#         para.append_child(aw.Run(doc, '('))
#         para.append_child(aw.Run(doc, '12'))
#         para.append_child(aw.Run(doc, ')'))
#         para.append_child(aw.Run(doc, ' months '))

#         has_updates = apply_inline_tracked_changes(doc, para, new_text, 'jp', datetime.now())

#         self.assertTrue(has_updates)
#         self.assertEqual(expected_tracking_text, para.get_text())

#     def test_multi_runs_3(self):
#         new_text = 'before the expiry of Eighteen (18) months from the Completion.'
#         expected_tracking_text = 'before the expiry of Twelve (12) Eighteen (18) months period from the Completion Completion.\r'

#         doc = aw.Document()
#         para = aw.Paragraph(doc)
#         para.append_child(aw.Run(doc, 'before the expiry of '))
#         para.append_child(aw.Run(doc, 'Twelve '))
#         para.append_child(aw.Run(doc, '('))
#         para.append_child(aw.Run(doc, '12'))
#         para.append_child(aw.Run(doc, ')'))
#         para.append_child(aw.Run(doc, ' months'))
#         para.append_child(aw.Run(doc, ' period'))
#         para.append_child(aw.Run(doc, ' from'))
#         para.append_child(aw.Run(doc, ' the'))
#         para.append_child(aw.Run(doc, ' Completion'))

#         has_updates = apply_inline_tracked_changes(doc, para, new_text, 'jp', datetime.now())

#         self.assertTrue(has_updates)
#         self.assertEqual(expected_tracking_text, para.get_text())

#     def test_multi_runs_4(self):
#         new_text = '– Unresolved Matter. For clarity, any adjustments arising from ‘Unresolved Matters’ shall be clearly explained in Schedule 2.'

#         expected_tracking_text = '– Unresolved Matter. The Net Purchase Price, as detailed Matter. For clarity, any adjustments arising from ‘Unresolved Matters’ shall be clearly explained in Schedule 2, shall be allocated among the Sellers in the proportions set out in Schedule 2, reflecting each Seller’s pro rata portion of the Sale Shares being sold by such Seller. 2.\r'

#         doc = aw.Document()
#         para = aw.Paragraph(doc)
#         para.append_child(aw.Run(doc, '– Unresolved Matter'))
#         para.append_child(aw.Run(doc, '.'))
#         para.append_child(aw.Run(doc, ' The '))
#         para.append_child(aw.Run(doc, 'Net '))
#         para.append_child(aw.Run(doc, 'Purchase Price'))
#         para.append_child(aw.Run(doc, ', as detailed in Schedule 2, '))
#         para.append_child(aw.Run(doc,
#                                  'shall be allocated among the Sellers in the proportions set out in Schedule 2, reflecting each Seller’s pro rata portion of the Sale Shares being sold by such Seller'))
#         para.append_child(aw.Run(doc, '.'))
#         para.append_child(aw.Run(doc, ''))

#         has_updates = apply_inline_tracked_changes(doc, para, new_text, 'jp', datetime.now())

#         self.assertTrue(has_updates)
#         self.assertEqual(expected_tracking_text, para.get_text())
