
from typing import Protocol
from uuid import uuid4
from datetime import datetime

from app.application.dtos.request import GenerateReportDto
from app.application.dtos.response import ReportDto


class ReportGeneratorService(Protocol):
    
    async def generate_report(
        self,
        report_type: str,
        from_date: str,
        to_date: str,
        metrics: list,
        format: str
    ) -> dict:

        ...


class GenerateCustomReportUseCase:

    
    def __init__(self, report_generator: ReportGeneratorService):
        self.report_generator = report_generator
    
    async def execute(self, dto: GenerateReportDto) -> ReportDto:

        report_result = await self.report_generator.generate_report(
            report_type=dto.report_type.value,
            from_date=dto.from_date.isoformat(),
            to_date=dto.to_date.isoformat(),
            metrics=[m.value for m in dto.metrics],
            format=dto.format.value
        )
        
        return ReportDto(
            id=uuid4(),
            report_type=dto.report_type.value,
            period={
                'from_date': dto.from_date,
                'to_date': dto.to_date
            },
            format=dto.format.value,
            file_url=report_result['file_url'],
            generated_at=datetime.utcnow()
        )