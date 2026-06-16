import math
from typing import Any, Dict


class StatisticalSignificanceCalculator:
    """Calculate statistical significance between control and variant groups."""

    def calculate(self, control_data: Dict[str, Any], variant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate improvement, confidence, p-value and significance."""
        try:
            improvement = self._calculate_improvement(control_data, variant_data)
            confidence, significance, p_value = self._calculate_significance(control_data, variant_data)

            return {
                'improvement': round(improvement, 1),
                'confidence': round(confidence, 1),
                'significance': significance,
                'p_value': round(p_value, 5)
            }
        except Exception as e:
            print(f"Error calculating statistical significance: {e}")
            return self._default_result()

    def _calculate_improvement(self, control_data: Dict[str, Any], variant_data: Dict[str, Any]) -> float:
        control_rate = control_data['conversion_rate']
        variant_rate = variant_data['conversion_rate']
        if control_rate <= 0:
            return 0.0
        return ((variant_rate - control_rate) / control_rate) * 100

    def _calculate_significance(self, control_data: Dict[str, Any], variant_data: Dict[str, Any]):
        p1 = control_data['conversion_rate'] / 100
        p2 = variant_data['conversion_rate'] / 100
        n1 = control_data['total_visitors']
        n2 = variant_data['total_visitors']

        if p1 <= 0 or p2 <= 0 or n1 <= 0 or n2 <= 0:
            return 0.0, False, 1.0

        p_pooled = (control_data['conversions'] + variant_data['conversions']) / (n1 + n2)
        se = (p_pooled * (1 - p_pooled) * (1 / n1 + 1 / n2)) ** 0.5
        z_score = abs(p2 - p1) / se if se > 0 else 0

        p_value = 2 * (1 - 0.5 * (1 + math.erf(z_score / math.sqrt(2))))
        confidence = (1 - p_value) * 100
        significance = confidence > 95
        return confidence, significance, p_value

    def _default_result(self) -> Dict[str, Any]:
        return {
            'improvement': 0,
            'confidence': 0,
            'significance': False,
            'p_value': 1
        }


def calculate_statistical_significance(control_data: Dict[str, Any], variant_data: Dict[str, Any]) -> Dict[str, Any]:
    """Backward-compatible wrapper around the class-based calculator."""
    return StatisticalSignificanceCalculator().calculate(control_data, variant_data)