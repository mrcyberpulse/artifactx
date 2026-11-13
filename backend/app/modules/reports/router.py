import uuid
import csv
import io
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import WorkspaceContext, workspace_access
from app.modules.workspaces.models import Role
from app.modules.vulnerabilities.models import Finding

router = APIRouter(prefix="/workspaces/{workspace_id}/reports", tags=["Reports"])

@router.get("/export/csv")
def export_csv(ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)), db: Session = Depends(get_db)):
    findings = db.scalars(select(Finding).where(Finding.workspace_id == ctx.workspace.id)).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Finding ID", "CVE", "Severity", "Risk Score", "Status"])
    for f in findings:
        writer.writerow([f.id, f.advisory.external_id, f.advisory.severity, f.risk_score, f.status])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=artifactx_report_{ctx.workspace.id}.csv"}
    )
@router.get("/export/pdf")
def export_pdf(ctx: WorkspaceContext = Depends(workspace_access(Role.viewer)), db: Session = Depends(get_db)):
    findings = db.scalars(select(Finding).where(Finding.workspace_id == ctx.workspace.id).order_by(Finding.risk_score.desc())).all()
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(f"ArtifactX Security Report - {ctx.workspace.name}", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Summary
    elements.append(Paragraph(f"Total Findings: {len(findings)}", styles['Heading2']))
    elements.append(Spacer(1, 12))

    # Table Data
    data = [["CVE", "Severity", "Risk Score", "Status"]]
    for f in findings:
        data.append([
            f.advisory.external_id, 
            f.advisory.severity or "UNKNOWN", 
            str(f.risk_score), 
            f.status
        ])

    if len(data) > 1:
        table = Table(data)
        table.setStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#171722')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f5f5f5')),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#a1a1aa'))
        ])
        elements.append(table)
    else:
        elements.append(Paragraph("No vulnerabilities found.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=artifactx_report_{ctx.workspace.id}.pdf"}
    )
