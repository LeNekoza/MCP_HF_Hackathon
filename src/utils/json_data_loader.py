import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class JsonDataLoader:
    """
    Utility class to load JSON analysis data from the filesystem.
    This replaces the hardcoded data in the interface with real file data.
    """

    def __init__(self, results_dir: Optional[str] = None):
        """
        Initialize the JSON data loader.

        Args:
            results_dir: Path to the results directory. If None, auto-detect.
        """
        if results_dir is None:
            # Auto-detect the results directory relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to project root and then to backend/result
            project_root = os.path.dirname(os.path.dirname(current_dir))
            results_dir = os.path.join(project_root, "backend", "result")

        self.results_dir = results_dir
        self._cache = {}
        self._cache_timestamp = {}
        self._cache_ttl = 300  # Cache for 5 minutes

        # Mapping of analysis types to their JSON filenames
        self.file_mapping = {
            "bed-occupancy": "bed_snapshot_result.json",
            "alos": "average_los_result.json",
            "staff-workload": "staff_load_result.json",
            "tool-utilisation": "tool_utilisation_result.json",
            "inventory-expiry": "inventory_expiry_result.json",
            "bed-census": "census_forecast_result.json",
            "elective-emergency": "admission_split_result.json",
            "los-prediction": "los_prediction_result.json",
        }

    def _is_cache_valid(self, analysis_type: str) -> bool:
        """Check if cached data is still valid."""
        if analysis_type not in self._cache_timestamp:
            return False

        cache_time = self._cache_timestamp[analysis_type]
        return (datetime.now() - cache_time).total_seconds() < self._cache_ttl

    def _load_json_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load JSON data from a file.

        Args:
            filename: Name of the JSON file to load

        Returns:
            Parsed JSON data or None if file doesn't exist or is invalid
        """
        try:
            file_path = os.path.join(self.results_dir, filename)

            if not os.path.exists(file_path):
                print(f"Warning: JSON file not found: {file_path}")
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data

        except (json.JSONDecodeError, IOError, OSError) as e:
            print(f"Error loading JSON file {filename}: {str(e)}")
            return None

    def get_analysis_data(self, analysis_type: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis data for a specific analysis type.

        Args:
            analysis_type: Type of analysis (e.g., 'bed-occupancy', 'alos', etc.)

        Returns:
            Analysis data dictionary or None if not available
        """
        # Check cache first
        if self._is_cache_valid(analysis_type) and analysis_type in self._cache:
            return self._cache[analysis_type]

        # Get filename for this analysis type
        filename = self.file_mapping.get(analysis_type)
        if not filename:
            print(f"Warning: No file mapping found for analysis type: {analysis_type}")
            return None

        # Load data from file
        data = self._load_json_file(filename)

        # Cache the data if successfully loaded
        if data is not None:
            self._cache[analysis_type] = data
            self._cache_timestamp[analysis_type] = datetime.now()

        return data

    def get_all_available_analyses(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all available analysis data.

        Returns:
            Dictionary mapping analysis types to their data
        """
        all_data = {}

        for analysis_type in self.file_mapping.keys():
            data = self.get_analysis_data(analysis_type)
            if data is not None:
                all_data[analysis_type] = data

        return all_data

    def refresh_cache(self, analysis_type: Optional[str] = None):
        """
        Refresh cached data for a specific analysis type or all types.

        Args:
            analysis_type: Specific analysis type to refresh, or None for all
        """
        if analysis_type is None:
            # Clear entire cache
            self._cache.clear()
            self._cache_timestamp.clear()
        else:
            # Clear specific cache entry
            self._cache.pop(analysis_type, None)
            self._cache_timestamp.pop(analysis_type, None)

    def is_data_available(self, analysis_type: str) -> bool:
        """
        Check if data is available for a specific analysis type.

        Args:
            analysis_type: Type of analysis to check

        Returns:
            True if data is available, False otherwise
        """
        filename = self.file_mapping.get(analysis_type)
        if not filename:
            return False

        file_path = os.path.join(self.results_dir, filename)
        return os.path.exists(file_path)

    def get_file_info(self, analysis_type: str) -> Dict[str, Any]:
        """
        Get information about the JSON file for an analysis type.

        Args:
            analysis_type: Type of analysis

        Returns:
            Dictionary with file information (path, exists, size, modified_time)
        """
        filename = self.file_mapping.get(analysis_type, "")
        file_path = os.path.join(self.results_dir, filename)

        info = {
            "filename": filename,
            "file_path": file_path,
            "exists": os.path.exists(file_path),
            "size": 0,
            "modified_time": None,
        }

        if info["exists"]:
            try:
                stat = os.stat(file_path)
                info["size"] = stat.st_size
                info["modified_time"] = datetime.fromtimestamp(stat.st_mtime)
            except OSError:
                pass

        return info


# Create a global instance for easy importing
_default_loader = None


def get_json_data_loader() -> JsonDataLoader:
    """Get the default JSON data loader instance."""
    global _default_loader
    if _default_loader is None:
        _default_loader = JsonDataLoader()
    return _default_loader


def load_analysis_data(analysis_type: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to load analysis data.

    Args:
        analysis_type: Type of analysis to load

    Returns:
        Analysis data or None if not available
    """
    loader = get_json_data_loader()
    return loader.get_analysis_data(analysis_type)
