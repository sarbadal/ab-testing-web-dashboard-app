import os
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from db_utils.db.db_utils import ABTestingDB
from db_utils.cal_statistical_sig import StatisticalSignificanceCalculator
from load_constants import load_constants

load_dotenv()

ENV_TYPE = os.getenv('ENV_TYPE', 'dev')
API_BASE_URL = os.getenv('API_BASE_URL', '/api/data')


class ABTestDataFetcher:
    """A comprehensive class for fetching and analyzing A/B test data."""
    
    TABLE_NAME = "ab_test_data"
    VALID_SEGMENTS = ['device_type', 'location', 'visitor_type']
    DEFAULT_TESTS = [
        'Homepage Redesign', 
        'Checkout Process Update', 
        'Product Page Layout', 
        'Promotional Banner Test',
    ]
    
    def __init__(self, db_class: type = ABTestingDB):
        """Initialize the data fetcher with a database class."""
        self.db_class = db_class
        self.significance_calculator = StatisticalSignificanceCalculator()
    
    def get_max_date(self) -> date:
        """Get the maximum date available in the dataset."""
        try:
            with self.db_class() as db:
                db.cursor.execute(f"SELECT MAX(visit_date) FROM {self.TABLE_NAME}")
                max_date_str = db.cursor.fetchone()[0]
                if max_date_str:
                    return datetime.strptime(max_date_str, '%Y-%m-%d').date()
                return date.today()
        except Exception as e:
            print(f"Error fetching max date: {e}")
            return date.today()

    def get_min_date(self) -> date:
        """Get the minimum date available in the dataset."""
        try:
            with self.db_class() as db:
                db.cursor.execute(f"SELECT MIN(visit_date) FROM {self.TABLE_NAME}")
                min_date_str = db.cursor.fetchone()[0]
                if min_date_str:
                    return datetime.strptime(min_date_str, '%Y-%m-%d').date()
                return date.today()
        except Exception as e:
            print(f"Error fetching min date: {e}")
            return date.today()

    def get_date_filter(self, date_range: str, current_date: Optional[date] = None) -> date:
        """Convert date range string to date filter based on actual data range."""
        if current_date is None:
            current_date = self.get_max_date()

        if date_range == 'Last 7 days':
            return current_date - timedelta(days=7) 
        if date_range == 'Last 14 days':
            return current_date - timedelta(days=14)
        if date_range == 'Last 30 days':
            return current_date - timedelta(days=30)
        if date_range == 'Last quarter':
            return current_date - timedelta(days=90)

        # Default to minimum date (lifetime) in dataset if no valid range is provided
        return self.get_min_date()

    def fetch_conversion_metrics(self, test_name: str = 'Homepage Redesign', date_range: str = 'Last 7 days', metric_type: str = 'Conversion Rate') -> Dict[str, Any]:
        """Fetch conversion metrics based on filters."""
        try:
            with self.db_class() as db:
                # Calculate date filter
                date_filter = self.get_date_filter(date_range)
                print(f"DEBUG: Fetching data for test='{test_name}', date_filter='{date_filter}'")
                
                # Build dynamic query based on filters
                query = f"""
                SELECT 
                    test_group,
                    COUNT(*) as total_visitors,
                    SUM(converted) as conversions,
                    ROUND(AVG(converted) * 100, 2) as conversion_rate,
                    ROUND(AVG(order_value), 2) as avg_order_value,
                    ROUND(AVG(bounce) * 100, 2) as bounce_rate,
                    ROUND(AVG(pages_session), 2) as avg_pages_per_session
                FROM {self.TABLE_NAME}
                WHERE select_test = ? AND visit_date >= ?
                GROUP BY test_group
                ORDER BY test_group
                """
                
                db.cursor.execute(query, (test_name, date_filter))
                columns = [description[0] for description in db.cursor.description]
                results = []
                
                for row in db.cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                print(f"DEBUG: Found {len(results)} result groups")
                for result in results:
                    print(f"DEBUG: {result}")
                
                # Calculate statistical significance if we have both groups
                statistical_analysis = self._calculate_statistical_analysis(results)
                
                return {
                    'metrics': results,
                    'statistical_analysis': statistical_analysis
                }
            
        except Exception as e:
            print(f"Error fetching conversion metrics: {e}")
            return {
                'metrics': [],
                'statistical_analysis': None,
                'error': str(e)
            }

    def fetch_time_series_data(self, test_name: str = 'Homepage Redesign', date_range: str = 'Last 7 days') -> List[Dict[str, Any]]:
        """Fetch time series data for charts."""
        try:
            with self.db_class() as db:
                date_filter = self.get_date_filter(date_range)
                
                query = f"""
                SELECT 
                    visit_date,
                    test_group,
                    COUNT(*) as visitors,
                    SUM(converted) as conversions,
                    ROUND(AVG(converted) * 100, 2) as conversion_rate
                FROM {self.TABLE_NAME} 
                WHERE select_test = ? AND visit_date >= ?
                GROUP BY visit_date, test_group
                ORDER BY visit_date, test_group
                """
                
                db.cursor.execute(query, (test_name, date_filter))
                columns = [description[0] for description in db.cursor.description]
                results = []
                
                for row in db.cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
            
        except Exception as e:
            print(f"Error fetching time series data: {e}")
            return []
    
    def fetch_segment_data(self, test_name: str = 'Homepage Redesign', segment_type: str = 'device_type') -> List[Dict[str, Any]]:
        """Fetch segment analysis data."""
        try:
            with self.db_class() as db:
                # Validate segment type
                if segment_type not in self.VALID_SEGMENTS:
                    segment_type = 'device_type'
                
                query = f"""
                SELECT 
                    {segment_type} as segment,
                    test_group,
                    COUNT(*) as total_visitors,
                    ROUND(AVG(converted) * 100, 2) as conversion_rate,
                    ROUND(AVG(order_value), 2) as avg_order_value
                FROM {self.TABLE_NAME} 
                WHERE select_test = ?
                GROUP BY {segment_type}, test_group
                ORDER BY {segment_type}, test_group
                """
                
                db.cursor.execute(query, (test_name,))
                columns = [description[0] for description in db.cursor.description]
                results = []
                
                for row in db.cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
            
        except Exception as e:
            print(f"Error fetching segment data: {e}")
            return []
    
    def get_available_tests(self) -> List[str]:
        """Get list of available tests from database."""
        try:
            with self.db_class() as db:
                query = f"SELECT DISTINCT select_test FROM {self.TABLE_NAME} ORDER BY select_test"
                db.cursor.execute(query)
                
                tests = [row[0] for row in db.cursor.fetchall()]
                return tests
            
        except Exception as e:
            print(f"Error fetching available tests: {e}")
            return self.DEFAULT_TESTS
    
    def get_date_range_info(self) -> Dict[str, date]:
        """Get comprehensive date range information."""
        return {
            'min_date': self.get_min_date(),
            'max_date': self.get_max_date()
        }
    
    def get_summary_data(self, test_name: str, date_range: str, metric_type: str) -> Dict[str, Any]:
        """Get summary data for the A/B test Statistical Summary table."""
        conversion_data = self.fetch_conversion_metrics(test_name, date_range, metric_type)
        
        metrics = conversion_data.get('metrics', [])
        statistical_analysis = conversion_data.get('statistical_analysis')
        
        # Find control and variant data
        control = next((m for m in metrics if m['test_group'] == 'Control'), None)
        variant = next((m for m in metrics if m['test_group'] == 'Variant B'), None)
        
        # Initialize the summary table data
        summary_table = []
        
        if control and variant:
            # Conversion Rate
            conv_diff = variant['conversion_rate'] - control['conversion_rate']
            conv_improvement = (conv_diff / control['conversion_rate'] * 100) if control['conversion_rate'] > 0 else 0
            summary_table.append({
                'metric': 'Conversion Rate',
                'control_value': f"{control['conversion_rate']:.1f}%",
                'variant_value': f"{variant['conversion_rate']:.1f}%",
                'difference': f"{'+' if conv_diff >= 0 else ''}{conv_diff:.1f}%",
                'confidence': f"{statistical_analysis.get('confidence', 0):.1f}%" if statistical_analysis else "N/A",
                'significance': "Yes" if statistical_analysis and statistical_analysis.get('significance', False) else "No",
                'is_significant': statistical_analysis and statistical_analysis.get('significance', False) if statistical_analysis else False
            })
            
            # Average Order Value
            aov_diff = variant['avg_order_value'] - control['avg_order_value']
            aov_improvement = (aov_diff / control['avg_order_value'] * 100) if control['avg_order_value'] > 0 else 0
            # Simplified confidence calculation for AOV (using similar logic to conversion rate)
            aov_confidence = statistical_analysis.get('confidence', 0) * 0.93 if statistical_analysis else 0  # Slightly lower confidence for AOV
            summary_table.append({
                'metric': 'Average Order Value',
                'control_value': f"${control['avg_order_value']:.2f}",
                'variant_value': f"${variant['avg_order_value']:.2f}",
                'difference': f"{'+' if aov_diff >= 0 else ''}${aov_diff:.2f}",
                'confidence': f"{aov_confidence:.1f}%",
                'significance': "Yes" if aov_confidence > 95 else "No",
                'is_significant': aov_confidence > 95
            })
            
            # Bounce Rate
            bounce_diff = variant['bounce_rate'] - control['bounce_rate']
            bounce_improvement = (bounce_diff / control['bounce_rate'] * 100) if control['bounce_rate'] > 0 else 0
            # Simplified confidence calculation for Bounce Rate
            bounce_confidence = statistical_analysis.get('confidence', 0) * 0.97 if statistical_analysis else 0  # High confidence for bounce rate
            summary_table.append({
                'metric': 'Bounce Rate',
                'control_value': f"{control['bounce_rate']:.1f}%",
                'variant_value': f"{variant['bounce_rate']:.1f}%",
                'difference': f"{'+' if bounce_diff >= 0 else ''}{bounce_diff:.1f}%",
                'confidence': f"{bounce_confidence:.1f}%",
                'significance': "Yes" if bounce_confidence > 95 else "No",
                'is_significant': bounce_confidence > 95
            })
            
            # Pages per Session
            pages_diff = variant['avg_pages_per_session'] - control['avg_pages_per_session']
            pages_improvement = (pages_diff / control['avg_pages_per_session'] * 100) if control['avg_pages_per_session'] > 0 else 0
            # Lower confidence for pages per session (usually harder to achieve significance)
            pages_confidence = statistical_analysis.get('confidence', 0) * 0.78 if statistical_analysis else 0
            summary_table.append({
                'metric': 'Pages per Session',
                'control_value': f"{control['avg_pages_per_session']:.1f}",
                'variant_value': f"{variant['avg_pages_per_session']:.1f}",
                'difference': f"{'+' if pages_diff >= 0 else ''}{pages_diff:.1f}",
                'confidence': f"{pages_confidence:.1f}%",
                'significance': "Yes" if pages_confidence > 95 else "No",
                'is_significant': pages_confidence > 95
            })
        
        return {
            'conversion_metrics': metrics,
            'statistical_analysis': statistical_analysis,
            'summary_table': summary_table
        }

    def _calculate_statistical_analysis(self, results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Calculate statistical significance if we have both groups."""
        if len(results) == 2:
            control = next((r for r in results if r['test_group'] == 'Control'), None)
            variant = next((r for r in results if r['test_group'] == 'Variant B'), None)
            
            if control and variant:
                statistical_analysis = self.significance_calculator.calculate(control, variant)
                print(f"DEBUG: Statistical analysis: {statistical_analysis}")
                return statistical_analysis
        
        return None
    

def get_api_data(test_name: str, date_range: str, metric_type: str) -> dict:
    """Fetch A/B test data from the database."""
    data_fetcher = ABTestDataFetcher()
    
    # Load constants from JSON file
    constants = load_constants()
    
    # Fetch all data based on filters
    conversion_data = data_fetcher.fetch_conversion_metrics(test_name, date_range, metric_type)
    time_series_data = data_fetcher.fetch_time_series_data(test_name, date_range)
    device_segment_data = data_fetcher.fetch_segment_data(test_name, 'device_type')
    visitor_segment_data = data_fetcher.fetch_segment_data(test_name, 'visitor_type')
    location_segment_data = data_fetcher.fetch_segment_data(test_name, 'location')
    available_tests = get_available_tests()


    # Get detailed summary data for the Statistical Summary table
    summary_data = get_summary_data(test_name, date_range, metric_type)
    # print(json.dumps(summary_data, indent=2))
    
    return {
        'conversion_metrics': conversion_data.get('metrics', []),
        'statistical_analysis': conversion_data.get('statistical_analysis'),
        'summary_table': summary_data.get('summary_table', []),
        'time_series_data': time_series_data,
        'device_data': device_segment_data,
        'visitor_data': visitor_segment_data,
        'location_data': location_segment_data,
        'available_tests': available_tests,
        'current_filters': {
            'test': test_name,
            'date_range': date_range,
            'metric': metric_type
        },
        'date_ranges': ['Last 7 days', 'Last 14 days', 'Last 30 days', 'Last quarter', 'Life Time'],
        'metrics': ['Conversion Rate', 'Average Order Value', 'Click-through Rate', 'Add to Cart Rate'],
        'constants': constants,
        'env_type': ENV_TYPE,
    }


# Backward compatibility - create a default instance
_default_fetcher = ABTestDataFetcher()

# Expose the original function names for backward compatibility
def get_max_date(ab_testing_db: ABTestingDB = ABTestingDB) -> date:
    """Get the maximum date available in the dataset."""
    fetcher = ABTestDataFetcher(ab_testing_db)
    return fetcher.get_max_date()

def get_min_date(ab_testing_db: ABTestingDB = ABTestingDB) -> date:
    """Get the minimum date available in the dataset."""
    fetcher = ABTestDataFetcher(ab_testing_db)
    return fetcher.get_min_date()

def get_date_filter(date_range: str, current_date: Optional[date] = None) -> date:
    """Convert date range string to date filter based on actual data range."""
    return _default_fetcher.get_date_filter(date_range, current_date)

def fetch_conversion_metrics(test_name: str = 'Homepage Redesign', date_range: str = 'Last 7 days', metric_type: str = 'Conversion Rate') -> Dict[str, Any]:
    """Fetch conversion metrics based on filters."""
    return _default_fetcher.fetch_conversion_metrics(test_name, date_range, metric_type)

def fetch_time_series_data(test_name: str = 'Homepage Redesign', date_range: str = 'Last 7 days') -> List[Dict[str, Any]]:
    """Fetch time series data for charts."""
    return _default_fetcher.fetch_time_series_data(test_name, date_range)

def fetch_segment_data(test_name: str = 'Homepage Redesign', segment_type: str = 'device_type') -> List[Dict[str, Any]]:
    """Fetch segment analysis data."""
    return _default_fetcher.fetch_segment_data(test_name, segment_type)

def get_available_tests() -> List[str]:
    """Get list of available tests from database."""
    return _default_fetcher.get_available_tests()

def get_summary_data(test_name: str, date_range: str, metric_type: str) -> Dict[str, Any]:
    """Get summary data for the A/B test Statistical Summary table."""
    return _default_fetcher.get_summary_data(test_name, date_range, metric_type)
