"""
PDF Generator Service

Generates three types of PDFs for each passenger:
1. MOU (Memo of Understanding) - with signature and responsibility statement
2. Affidavit - with signature and travel category license
3. Reservation - with passenger and trip details

All PDFs are automatically uploaded to S3 and linked to the passenger.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime
import io
import os
from services.file_manager import file_manager
from constants import RESPONSIBILITY_STATEMENT


class PDFGenerator:
    """Generate passenger PDFs and upload to S3"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
        
        # Signature style
        self.styles.add(ParagraphStyle(
            name='SignatureStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=6
        ))
    
    def generate_mou(self, passenger, trip, signature_path=None):
        """
        Generate Memo of Understanding PDF
        
        Args:
            passenger: Passenger model instance
            trip: Trip model instance
            signature_path: Local path to signature image (optional)
        
        Returns:
            tuple: (pdf_buffer, s3_key) or (None, None) if error
        """
        buffer = io.BytesIO()
        
        try:
            # Create PDF
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)
            
            story = []
            
            # Title
            title = Paragraph("MEMORANDUM OF UNDERSTANDING", self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 0.3*inch))
            
            # Trip Information
            trip_info = f"""
            <b>Trip:</b> {trip.destination or 'N/A'}<br/>
            <b>Travel Dates:</b> {trip.start_date.strftime('%B %d, %Y') if trip.start_date else 'TBD'} 
            to {trip.end_date.strftime('%B %d, %Y') if trip.end_date else 'TBD'}<br/>
            <b>Category:</b> {trip.travel_category or 'General Travel'}<br/>
            """
            story.append(Paragraph(trip_info, self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
            
            # Passenger Information
            contact = passenger.contact
            passenger_info = f"""
            <b>Passenger Name:</b> {contact.firstname} {contact.lastname}<br/>
            <b>Email:</b> {contact.email}<br/>
            <b>Phone:</b> {contact.phone or 'Not provided'}<br/>
            <b>Date of Birth:</b> {passenger.date_of_birth.strftime('%B %d, %Y') if passenger.date_of_birth else 'Not provided'}<br/>
            """
            story.append(Paragraph(passenger_info, self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*inch))
            
            # Responsibility Statement (from constants.py)
            story.append(Paragraph("<b>Responsibility Statement</b>", self.styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            # Split the responsibility statement into paragraphs for better formatting
            responsibility_paragraphs = RESPONSIBILITY_STATEMENT.split('\n\n')
            for para_text in responsibility_paragraphs:
                if para_text.strip():
                    story.append(Paragraph(para_text.strip(), self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*inch))
            
            # Acknowledgment
            acknowledgment = """
            By signing below, the traveler acknowledges that they have read, understood, and agree to abide by 
            the terms and conditions outlined in this Memorandum of Understanding.
            """
            story.append(Paragraph(acknowledgment, self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*inch))
            
            # Signature section
            signature_data = [
                ['Passenger Signature:', '', 'Date:'],
                ['', '', datetime.now().strftime('%B %d, %Y')]
            ]
            
            # If signature image provided, add it
            if signature_path and os.path.exists(signature_path):
                try:
                    sig_img = Image(signature_path, width=2*inch, height=1*inch)
                    signature_data[0][1] = sig_img
                except Exception as e:
                    print(f"Error adding signature image: {e}")
                    signature_data[0][1] = '_' * 40
            else:
                signature_data[0][1] = '_' * 40
            
            sig_table = Table(signature_data, colWidths=[2*inch, 3*inch, 1.5*inch])
            sig_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            story.append(sig_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Footer
            footer = f"""
            <i>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i><br/>
            Document ID: MOU-{passenger.id}-{int(datetime.now().timestamp())}
            """
            story.append(Paragraph(footer, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.seek(0)
            
            # Upload to S3
            passenger_name = f"{contact.firstname}_{contact.lastname}"
            s3_key = file_manager.build_s3_path(
                trip.name,
                passenger_name,
                'documents',
                f'mou_{int(datetime.now().timestamp())}.pdf'
            )
            
            success = file_manager.upload_file(
                buffer,
                s3_key,
                content_type='application/pdf',
                make_public=False
            )
            
            if success:
                return pdf_bytes, s3_key
            else:
                return None, None
                
        except Exception as e:
            print(f"Error generating MOU: {e}")
            return None, None
        finally:
            buffer.close()
    
    def generate_affidavit(self, passenger, trip, signature_path=None):
        """
        Generate Affidavit PDF
        
        Uses the same signature as MOU and includes travel_category_license
        (which is copied from Trip.travel_category to passenger.travel_category_license)
        
        Args:
            passenger: Passenger model instance
            trip: Trip model instance
            signature_path: Local path to signature image (optional)
        
        Returns:
            tuple: (pdf_buffer, s3_key) or (None, None) if error
        """
        buffer = io.BytesIO()
        
        try:
            # Create PDF
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)
            
            story = []
            
            # Title
            title = Paragraph("TRAVEL AFFIDAVIT", self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 0.3*inch))
            
            contact = passenger.contact
            
            # Affiant Information
            affiant_info = f"""
            <b>Affiant Information:</b><br/>
            <b>Full Name:</b> {contact.firstname} {contact.lastname}<br/>
            <b>Date of Birth:</b> {passenger.date_of_birth.strftime('%B %d, %Y') if passenger.date_of_birth else 'Not provided'}<br/>
            <b>Email:</b> {contact.email}<br/>
            <b>Phone:</b> {contact.phone or 'Not provided'}<br/>
            """
            story.append(Paragraph(affiant_info, self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
            
            # Trip Information
            trip_info = f"""
            <b>Trip Details:</b><br/>
            <b>Destination:</b> {trip.destination or 'N/A'}<br/>
            <b>Travel Dates:</b> {trip.start_date.strftime('%B %d, %Y') if trip.start_date else 'TBD'} 
            to {trip.end_date.strftime('%B %d, %Y') if trip.end_date else 'TBD'}<br/>
            <b>Travel Category:</b> {passenger.travel_category_license or trip.travel_category or 'General'}<br/>
            """
            story.append(Paragraph(trip_info, self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*inch))
            
            # Affidavit Text
            affidavit_text = """
            <b>AFFIDAVIT:</b><br/><br/>
            
            I, the undersigned, being of lawful age and under oath, do hereby affirm and declare the following:<br/><br/>
            
            <b>1. Identity and Capacity:</b> I am the individual named above and I am voluntarily participating 
            in the travel program described herein. I have the legal capacity to enter into this agreement.<br/><br/>
            
            <b>2. Health Declaration:</b> I certify that I am in good health and physically capable of participating 
            in the planned activities. I have disclosed all relevant medical conditions and understand the potential 
            risks involved in travel.<br/><br/>
            
            <b>3. Travel Documents:</b> I affirm that I possess or will obtain all necessary travel documents, 
            including a valid passport and any required visas, before the departure date.<br/><br/>
            
            <b>4. Financial Responsibility:</b> I acknowledge my responsibility to pay all fees associated with 
            this trip according to the agreed-upon payment schedule.<br/><br/>
            
            <b>5. Code of Conduct:</b> I agree to conduct myself in a manner that is respectful, lawful, and 
            consistent with the stated purpose and guidelines of this travel program.<br/><br/>
            
            <b>6. Release of Liability:</b> I understand and accept the inherent risks of international travel. 
            I hereby release and hold harmless the trip organizers, vendors, and their representatives from any 
            and all claims arising from my participation.<br/><br/>
            
            <b>7. Accuracy of Information:</b> I certify that all information provided in connection with this 
            trip is true, accurate, and complete to the best of my knowledge.<br/><br/>
            """
            story.append(Paragraph(affidavit_text, self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*inch))
            
            # Oath
            oath = """
            I declare under penalty of perjury that the foregoing is true and correct.
            """
            story.append(Paragraph(oath, self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*inch))
            
            # Signature section
            signature_data = [
                ['Affiant Signature:', '', 'Date:'],
                ['', '', datetime.now().strftime('%B %d, %Y')]
            ]
            
            # If signature image provided, add it
            if signature_path and os.path.exists(signature_path):
                try:
                    sig_img = Image(signature_path, width=2*inch, height=1*inch)
                    signature_data[0][1] = sig_img
                except Exception as e:
                    print(f"Error adding signature image: {e}")
                    signature_data[0][1] = '_' * 40
            else:
                signature_data[0][1] = '_' * 40
            
            sig_table = Table(signature_data, colWidths=[2*inch, 3*inch, 1.5*inch])
            sig_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            story.append(sig_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Footer
            footer = f"""
            <i>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i><br/>
            Document ID: AFFIDAVIT-{passenger.id}-{int(datetime.now().timestamp())}
            """
            story.append(Paragraph(footer, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.seek(0)
            
            # Upload to S3
            passenger_name = f"{contact.firstname}_{contact.lastname}"
            s3_key = file_manager.build_s3_path(
                trip.name,
                passenger_name,
                'documents',
                f'affidavit_{int(datetime.now().timestamp())}.pdf'
            )
            
            success = file_manager.upload_file(
                buffer,
                s3_key,
                content_type='application/pdf',
                make_public=False
            )
            
            if success:
                return pdf_bytes, s3_key
            else:
                return None, None
                
        except Exception as e:
            print(f"Error generating affidavit: {e}")
            return None, None
        finally:
            buffer.close()
    
    def generate_reservation(self, passenger, trip):
        """
        Generate Reservation Confirmation PDF
        
        Args:
            passenger: Passenger model instance
            trip: Trip model instance
        
        Returns:
            tuple: (pdf_buffer, s3_key) or (None, None) if error
        """
        buffer = io.BytesIO()
        
        try:
            # Create PDF
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)
            
            story = []
            
            # Title
            title = Paragraph("TRIP RESERVATION CONFIRMATION", self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 0.3*inch))
            
            contact = passenger.contact
            
            # Confirmation header
            confirmation_number = f"RES-{passenger.id}-{int(datetime.now().timestamp())}"
            header = f"""
            <b>Confirmation Number:</b> {confirmation_number}<br/>
            <b>Reservation Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>
            """
            story.append(Paragraph(header, self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*inch))
            
            # Trip Details
            story.append(Paragraph("<b>TRIP DETAILS</b>", self.styles['Heading2']))
            trip_details = f"""
            <b>Destination:</b> {trip.destination or 'To be announced'}<br/>
            <b>Trip Name:</b> {trip.name or 'N/A'}<br/>
            <b>Departure Date:</b> {trip.start_date.strftime('%B %d, %Y') if trip.start_date else 'TBD'}<br/>
            <b>Return Date:</b> {trip.end_date.strftime('%B %d, %Y') if trip.end_date else 'TBD'}<br/>
            <b>Duration:</b> {trip.nights_total or 'TBD'} nights<br/>
            <b>Lodging:</b> {trip.lodging or 'To be confirmed'}<br/>
            <b>Category:</b> {trip.travel_category or 'General Travel'}<br/>
            """
            story.append(Paragraph(trip_details, self.styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
            
            # Passenger Information
            story.append(Paragraph("<b>PASSENGER INFORMATION</b>", self.styles['Heading2']))
            passenger_details = f"""
            <b>Name:</b> {contact.firstname} {contact.lastname}<br/>
            <b>Email:</b> {contact.email}<br/>
            <b>Phone:</b> {contact.phone or 'Not provided'}<br/>
            <b>Date of Birth:</b> {passenger.date_of_birth.strftime('%B %d, %Y') if passenger.date_of_birth else 'Not provided'}<br/>
            """
            if contact.address:
                passenger_details += f"""
                <b>Address:</b> {contact.address}<br/>
                """
                if contact.city and contact.state:
                    passenger_details += f"{contact.city}, {contact.state} {contact.postal_code or ''}<br/>"
            
            story.append(Paragraph(passenger_details, self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*inch))
            
            # Pricing (if available)
            if trip.trip_standard_level_pricing:
                story.append(Paragraph("<b>PRICING</b>", self.styles['Heading2']))
                pricing = f"""
                <b>Standard Level:</b> ${trip.trip_standard_level_pricing:,.2f}<br/>
                """
                if trip.deposit_date:
                    pricing += f"<b>Deposit Due:</b> {trip.deposit_date.strftime('%B %d, %Y')}<br/>"
                if trip.final_payment:
                    pricing += f"<b>Final Payment Due:</b> {trip.final_payment.strftime('%B %d, %Y')}<br/>"
                
                story.append(Paragraph(pricing, self.styles['CustomBody']))
                story.append(Spacer(1, 0.2*inch))
            
            # Important Information
            story.append(Paragraph("<b>IMPORTANT INFORMATION</b>", self.styles['Heading2']))
            important_info = """
            <b>Travel Documents:</b> Please ensure your passport is valid for at least 6 months beyond 
            the return date. Check visa requirements for your destination.<br/><br/>
            
            <b>Travel Insurance:</b> We strongly recommend purchasing comprehensive travel insurance 
            to protect your investment.<br/><br/>
            
            <b>Health Requirements:</b> Consult with your healthcare provider regarding any necessary 
            vaccinations or health precautions for your destination.<br/><br/>
            
            <b>Contact Information:</b> For questions or changes to your reservation, please contact 
            us at your earliest convenience.<br/><br/>
            """
            story.append(Paragraph(important_info, self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*inch))
            
            # Footer
            footer = f"""
            <i>Thank you for choosing to travel with us!</i><br/><br/>
            Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
            Document ID: {confirmation_number}
            """
            story.append(Paragraph(footer, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.seek(0)
            
            # Upload to S3
            passenger_name = f"{contact.firstname}_{contact.lastname}"
            s3_key = file_manager.build_s3_path(
                trip.name,
                passenger_name,
                'documents',
                f'reservation_{int(datetime.now().timestamp())}.pdf'
            )
            
            success = file_manager.upload_file(
                buffer,
                s3_key,
                content_type='application/pdf',
                make_public=False
            )
            
            if success:
                return pdf_bytes, s3_key
            else:
                return None, None
                
        except Exception as e:
            print(f"Error generating reservation: {e}")
            return None, None
        finally:
            buffer.close()
    
    def generate_all_pdfs(self, passenger, trip, signature_path=None):
        """
        Generate all three PDFs for a passenger
        
        Args:
            passenger: Passenger model instance
            trip: Trip model instance
            signature_path: Local path to signature image (optional)
        
        Returns:
            dict: Dictionary with s3_keys for each PDF type
        """
        results = {
            'mou': None,
            'affidavit': None,
            'reservation': None
        }
        
        # Generate MOU
        _, mou_key = self.generate_mou(passenger, trip, signature_path)
        if mou_key:
            results['mou'] = mou_key
        
        # Generate Affidavit
        _, affidavit_key = self.generate_affidavit(passenger, trip, signature_path)
        if affidavit_key:
            results['affidavit'] = affidavit_key
        
        # Generate Reservation
        _, reservation_key = self.generate_reservation(passenger, trip)
        if reservation_key:
            results['reservation'] = reservation_key
        
        return results


# Global instance
pdf_generator = PDFGenerator()