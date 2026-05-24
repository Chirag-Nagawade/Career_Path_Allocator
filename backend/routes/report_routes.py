from flask import Blueprint, send_file, jsonify
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart

from routes.auth_routes import token_required
from db import users_collection, predictions_collection, academic_marks_collection, psychometric_data_collection
from excel_processor import ExcelDataProcessor
from utils.recommendation_utils import get_recommended_institutions

report_routes = Blueprint('report_routes', __name__)
processor = ExcelDataProcessor()

def create_bar_chart(data, labels, title, min_val=0, max_val=100):
    drawing = Drawing(220, 150)
    bc = VerticalBarChart()
    bc.x = 30
    bc.y = 30
    bc.height = 100
    bc.width = 170
    bc.data = [data]
    bc.strokeColor = colors.white
    bc.valueAxis.valueMin = min_val
    bc.valueAxis.valueMax = max_val
    bc.valueAxis.valueStep = 20
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = labels
    bc.bars[0].fillColor = colors.HexColor('#5F8D4E') 
    drawing.add(bc)
    return drawing

def create_horizontal_bar_chart(data, labels):
    drawing = Drawing(220, 150)
    bc = HorizontalBarChart()
    bc.x = 60 # Leave space for labels on the left
    bc.y = 20
    bc.width = 140
    bc.height = 110
    bc.data = [data]
    bc.strokeColor = colors.white
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 5
    bc.valueAxis.valueStep = 1
    bc.categoryAxis.labels.boxAnchor = 'e'
    bc.categoryAxis.labels.dx = -5
    bc.categoryAxis.categoryNames = labels
    bc.bars[0].fillColor = colors.HexColor('#C6A969') # Gold for variety
    drawing.add(bc)
    return drawing

@report_routes.route('/download', methods=['GET'])
@token_required
def download_pdf_report(current_user):
    try:
        email = current_user['email']
        full_name = current_user.get('full_name', 'Student')
        
        # Gather all user data
        pred_doc = predictions_collection.find_one({"user_email": email}, sort=[("timestamp", -1)])
        acc = academic_marks_collection.find_one({"user_email": email}, sort=[("_id", -1)])
        psy = psychometric_data_collection.find_one({"user_email": email}, sort=[("_id", -1)])
        
        if not pred_doc or not acc or not psy:
            return jsonify({"status": False, "message": "Incomplete assessment data. Please complete the assessment."}), 400

        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=30, bottomMargin=30)

        Story = []
        styles = getSampleStyleSheet()
        
        # Premium Colors & Styles
        sage_green = colors.HexColor('#5F8D4E')
        dark_text = colors.HexColor('#2B2B2B')
        bg_cream = colors.HexColor('#F9F7F2')
        
        styles.add(ParagraphStyle(
            name='MargIntelHeader', 
            parent=styles['Heading1'], 
            textColor=sage_green, 
            fontSize=26, 
            alignment=1, 
            spaceAfter=5
        ))
        styles.add(ParagraphStyle(
            name='SubTitle', 
            parent=styles['Normal'], 
            textColor=colors.grey, 
            fontSize=10, 
            alignment=1, 
            spaceAfter=30
        ))
        styles.add(ParagraphStyle(
            name='SectionHeader', 
            parent=styles['Heading2'], 
            textColor=dark_text, 
            fontSize=14, 
            spaceBefore=15, 
            spaceAfter=10, 
            leftIndent=0,
            borderPadding=8,
            backColor=bg_cream,
            borderColor=sage_green,
            borderWidth=1,
            borderRadius=5
        ))
        styles.add(ParagraphStyle(name='NormalText', parent=styles['Normal'], fontSize=10, spaceAfter=8, leading=14))
        styles.add(ParagraphStyle(name='BulletPoint', parent=styles['Normal'], fontSize=10, leftIndent=20, spaceAfter=6, bulletText='\u2022'))

        # 1. Header Section
        Story.append(Paragraph("MARGINTEL CAREER BLUEPRINT", styles['MargIntelHeader']))
        Story.append(Paragraph("Advanced AI-Driven Career Allocation & Academic Roadmap", styles['SubTitle']))
        
        # User Info Table
        data = [
            [Paragraph(f"<b>Student Name:</b> {full_name}", styles['NormalText']), 
             Paragraph(f"<b>Standard:</b> {acc.get('standard', '10th')}", styles['NormalText'])],
            [Paragraph(f"<b>Email:</b> {email}", styles['NormalText']), 
             Paragraph(f"<b>Report Date:</b> {pred_doc.get('timestamp', 'N/A')[:10]}", styles['NormalText'])]
        ]
        t = Table(data, colWidths=[250, 250])
        t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        Story.append(t)
        Story.append(Spacer(1, 20))

        # 2. Executive Career Summary (with matching cards)
        Story.append(Paragraph("1. Career Matching Blueprint", styles['SectionHeader']))
        tc = pred_doc.get('top_careers', [])
        primary = tc[0] if tc else {}
        career_name = primary.get('career', primary.get('Career_Name', 'Unknown'))
        
        # Mapping for display
        for index, p in enumerate(tc[:3]): # Top 3 matches
            name = p.get('career', p.get('Career_Name', 'Unknown'))
            prob = p.get('match_score', int((p.get('probability', 0)) * 100))
            is_top = (index == 0)
            
            # Use Paragraph for 'Why this fits' to allow word wrapping inside the table
            reason = p.get('reason', f"Your academic profile in {acc.get('standard')} and psychometric traits align perfectly with the core competencies required for a successful career in {name}.")
            
            card_data = [
                [Paragraph(f"<b>{'TOP CHOICE: ' if is_top else 'MATCH: '}{name}</b>", ParagraphStyle(name='CardTitle', parent=styles['Normal'], fontSize=11, textColor=sage_green if is_top else dark_text))],
                [Paragraph(f"<b>Match Score:</b> {prob}%", styles['NormalText'])],
                [Paragraph(f"<b>Why this fits:</b> {reason}", styles['NormalText'])]
            ]
            
            card_table = Table(card_data, colWidths=[500])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FCFBF8') if is_top else colors.white),
                ('BOX', (0,0), (-1,-1), 1, sage_green if is_top else colors.lightgrey),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            Story.append(card_table)
            Story.append(Spacer(1, 10))

        # 3. Academic & Psychometric Charts (Side by Side)
        Story.append(Paragraph("2. Performance Visualizers", styles['SectionHeader']))
        
        # Academic Data
        marks_data = []
        marks_labels = []
        exclude = ['_id', 'user_email', 'standard', 'timestamp']
        for k, v in acc.items():
            if k not in exclude:
                marks_labels.append(k.replace('_', ' ').capitalize())
                marks_data.append(float(v))
        
        # Psychometric Data
        psy_data = []
        psy_labels = []
        mapping = {'logical': 'Logical', 'creative': 'Creative', 'communication': 'Comm.', 'leadership': 'Lead.', 'detail': 'Detail'}
        for k, v in psy.items():
            if k in mapping:
                psy_labels.append(mapping[k])
                psy_data.append(int(v))

        # Charts Table
        bar_chart = create_bar_chart(marks_data, marks_labels, "Academic Profile")
        psy_chart = create_horizontal_bar_chart(psy_data, psy_labels)
        
        chart_table = Table([[bar_chart, psy_chart]], colWidths=[250, 250])
        chart_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        Story.append(chart_table)
        Story.append(Spacer(1, 10))

        # 4. Recommended Educational Institutions
        Story.append(Paragraph("3. Recommended Educational Institutions", styles['SectionHeader']))
        Story.append(Paragraph(f"Top 5 institutions matched to your <b>{career_name}</b> path:", styles['NormalText']))
        
        standard = acc.get('standard', '10th')
        colleges = get_recommended_institutions(career_name, standard, limit=5)
        
        if colleges:
            # Custom style for table cells to handle wrapping
            cell_style = ParagraphStyle(name='TableCell', parent=styles['Normal'], fontSize=8, leading=10)
            
            college_data = [["Institution Name", "City", "Recommended Path", "Min. Cutoff"]]
            for col in colleges:
                # Wrap name and path in Paragraphs to prevent overflow
                name_p = Paragraph(col['name'], cell_style)
                path_str = col.get('recommended_path', 'General').replace('Higher Secondary (11th & 12th) - ', 'HSC (11-12) - ').replace('Undergraduate Degree for ', '')
                path_p = Paragraph(path_str, cell_style)
                
                college_data.append([name_p, col['city'], path_p, col['cutoff']])
            
            ct = Table(college_data, colWidths=[140, 60, 220, 80])
            ct.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), sage_green),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BACKGROUND', (0,1), (-1,-1), bg_cream),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
            ]))
            Story.append(ct)
        else:
            Story.append(Paragraph("No specific institutions found for this path in current regions.", styles['NormalText']))

        # 5. Strategic Roadmap
        # Removed PageBreak() here to reduce unnecessary space
        Story.append(Paragraph("4. Strategic Career Roadmap", styles['SectionHeader']))
        
        # Generate actions using processor
        marks_input = {k: float(v) for k, v in acc.items() if k not in exclude}
        psy_input = {k: int(v) for k, v in psy.items() if k in mapping}
        interests = [psy.get('interest1', ''), psy.get('interest2', ''), psy.get('interest3', '')]
        interests = [i for i in interests if i]
        
        actions = processor._get_recommended_actions(marks_input, psy_input, interests, standard)
        
        roadmap_cats = {
            "Academic Focus": [a for a in actions if '%' in a],
            "Professional Traits": [a for a in actions if '/5' in a],
            "Next Strategic Steps": [a for a in actions if ('TIMELINE' in a or 'Success' in a or 'Recommended' in a) and "mastering fundamentals" not in a.lower()]
        }

        for cat, items in roadmap_cats.items():
            if items:
                Story.append(Paragraph(f"<b>\u203A {cat}</b>", styles['NormalText']))
                for item in items:
                    import re
                    clean_item = re.sub(r'[^\x00-\x7F]+', '', item) 
                    Story.append(Paragraph(clean_item, styles['BulletPoint']))
                Story.append(Spacer(1, 10))

        # Footer Branding
        Story.append(Spacer(1, 40))
        Story.append(Paragraph("<hr/>", styles['NormalText']))
        Story.append(Paragraph("© 2026 MargIntel - Powered by Advanced Machine Learning Assessment Tools", styles['SubTitle']))

        # Build PDF
        doc.build(Story)
        buffer.seek(0)
        return send_file(
            buffer, 
            as_attachment=True, 
            download_name=f"MargIntel_Report_{full_name.replace(' ', '_')}.pdf", 
            mimetype='application/pdf'
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": False, "message": str(e)}), 500
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": False, "message": str(e)}), 500

