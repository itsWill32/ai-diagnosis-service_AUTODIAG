
from dataclasses import dataclass
from enum import Enum


class Currency(str, Enum):
    MXN = "MXN"
    USD = "USD"


@dataclass(frozen=True)
class CostEstimate:

    min_cost: float
    max_cost: float
    currency: Currency = Currency.MXN
    
    def __post_init__(self):

        if not isinstance(self.min_cost, (int, float)):
            raise ValueError(
                f"min_cost debe ser numérico, recibido: {type(self.min_cost)}"
            )
        
        if not isinstance(self.max_cost, (int, float)):
            raise ValueError(
                f"max_cost debe ser numérico, recibido: {type(self.max_cost)}"
            )
        
        if not isinstance(self.currency, Currency):
            raise ValueError(
                f"currency debe ser Currency enum, recibido: {type(self.currency)}"
            )
        
        object.__setattr__(self, 'min_cost', float(self.min_cost))
        object.__setattr__(self, 'max_cost', float(self.max_cost))
        
        if self.min_cost < 0:
            raise ValueError(f"min_cost no puede ser negativo: {self.min_cost}")
        
        if self.max_cost < 0:
            raise ValueError(f"max_cost no puede ser negativo: {self.max_cost}")
        
        if self.min_cost > self.max_cost:
            raise ValueError(
                f"min_cost ({self.min_cost}) no puede ser mayor que max_cost ({self.max_cost})"
            )
    
    @classmethod
    def create(cls, min_cost: float, max_cost: float, 
               currency: str = "MXN") -> 'CostEstimate':

        currency_enum = Currency(currency.upper())
        return cls(
            min_cost=min_cost,
            max_cost=max_cost,
            currency=currency_enum
        )
    
    @classmethod
    def create_single_estimate(cls, estimated_cost: float, 
                               margin_percentage: float = 20.0,
                               currency: str = "MXN") -> 'CostEstimate':

        if margin_percentage < 0 or margin_percentage > 100:
            raise ValueError(
                f"margin_percentage debe estar entre 0 y 100, recibido: {margin_percentage}"
            )
        
        margin = estimated_cost * (margin_percentage / 100.0)
        min_cost = max(0.0, estimated_cost - margin)
        max_cost = estimated_cost + margin
        
        return cls.create(min_cost, max_cost, currency)
    
    def get_min_cost(self) -> float:
        return self.min_cost
    
    def get_max_cost(self) -> float:
        return self.max_cost
    
    def get_average_cost(self) -> float:

        return (self.min_cost + self.max_cost) / 2.0
    
    def get_currency(self) -> str:
        return self.currency.value
    
    def get_range_width(self) -> float:

        return self.max_cost - self.min_cost
    
    def is_expensive(self, threshold: float = 5000.0) -> bool:

        return self.get_average_cost() > threshold
    
    def format_range(self, include_currency: bool = True) -> str:

        if include_currency:
            return (
                f"${self.min_cost:,.2f} - ${self.max_cost:,.2f} {self.currency.value}"
            )
        else:
            return f"${self.min_cost:,.2f} - ${self.max_cost:,.2f}"
    
    def __str__(self) -> str:
        return self.format_range(include_currency=True)
    
    def __repr__(self) -> str:
        return (
            f"CostEstimate(min={self.min_cost:.2f}, "
            f"max={self.max_cost:.2f}, "
            f"currency={self.currency.value})"
        )