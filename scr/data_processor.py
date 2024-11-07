import pandas as pd
import re

class DataProcessor:
    def __init__(self, data, experiment_type, measurement_source):
        """
        Initialize the DataProcessor for a specific experiment.

        Parameters:
        - data: The raw data (as a DataFrame).
        - experiment_type: 'RefLab' or 'MPA' to specify the experiment type.
        - column_mappings: Dictionary to map raw column names to standardized names.
        """
        self.raw_data = data
        self.processed_data = pd.DataFrame()
        self.experiment_type = experiment_type
        self.measurement_source = measurement_source

    def process(self):
        """Process the data based on the experiment type."""
        if self.experiment_type == 'ref_lab':
            return self.process_reflab_data()
        elif self.experiment_type == 'mpa':
            return self.process_mpa_data()
        else:
            raise ValueError("Unsupported experiment type")

    def process_reflab_data(self):
        """Process data specific to the RefLab experiment."""
        # As there is much more information stored in the xml files, only select the "raw" datapoints (LINK_MODEL_BASED element for motion capture, and MUSCLE_ACTIVITY_NORMALIZED for EMG)
        self.raw_data = self.raw_data[(self.raw_data['type'] == 'LINK_MODEL_BASED') | (self.raw_data['folder'] == 'MUSCLE_ACTIVITY_NORMALIZED') ]
        # Sort the dataframe by start time
        self.raw_data = self.raw_data.sort_values(by='time_start', ascending=True)
        self.raw_data['experiment'] = self.experiment_type
        
        # 
        unique_values_owner = self.raw_data['owner'].unique().tolist()
        for owner in unique_values_owner:    
            mask = (self.raw_data['owner'] == owner)
            self.raw_data.loc[mask, 'stroke_nr'] = range(len(self.raw_data[mask]))
        #    self.raw_data[self.raw_data['owner'] == owner]['stroke_nr'] = range(len(self.raw_data[self.raw_data['owner'] == owner]))
        
        # Create a column that contains the cyclic index for each row (before exploding)
        self.raw_data['time_index'] = self.raw_data['data'].apply(lambda x: range(len(x)))

        # Explode both 'col1' and 'cyclic_index' to expand the DataFrame
        self.temp_data = self.raw_data.explode(['data', 'time_index']).reset_index(drop=True)
        
        # Explode the DataFrame   
                
        self.processed_data['experiment'] = self.temp_data['experiment']
        self.processed_data['source'] = self.measurement_source
        self.processed_data['owner'] =  self.temp_data['owner']

        # Regex pattern to extract the user ID
        pattern = r'(\d{2,3})\.\w+$'

        # Extract the bpm and save it to a new column
        self.processed_data['bpm'] = self.processed_data['owner'].str.extract(pattern).astype(int)
        
        self.processed_data['stroke_nr'] = self.temp_data['stroke_nr']
        self.processed_data['bow_stroke'] = self.temp_data['event_sequence']
        self.processed_data['location'] = self.temp_data['name']
        self.processed_data['axis'] = self.temp_data['component_value']
        self.processed_data['frame_start'] = self.temp_data['frame_start']
        self.processed_data['frame_end'] = self.temp_data['frame_end']
        self.processed_data['time_start'] = self.temp_data['time_start']
        self.processed_data['time_end'] = self.temp_data['time_end']
        self.processed_data['frames'] = self.temp_data['frames']
        self.processed_data['data'] = self.temp_data['data']
        self.processed_data['time_index'] = self.temp_data['time_index']

        return self.processed_data

    def process_mpa_data(self):
        """Process data specific to the MPA experiment."""
        
        # Handle participant info, no bow stroke, 100 data points
        data_list = []
        # Iteriere über die Spalten (beginnend bei der zweiten Spalte, da die erste Spalte die 'cycle'-Daten enthält)
        for i, col in enumerate(self.raw_data.columns[1:], start=0):  # Start bei 0 für 'stroke_nr'
            col_index = self.raw_data.columns.get_loc(col) 
            experiment_data = self.raw_data.iloc[4:, col_index]  # Daten ab Zeile 6
            cycle_data = self.raw_data.iloc[4:, 0]  # 'cycle' ist in der ersten Spalte
            axis = self.raw_data.iloc[3, col_index]
            # Extract participant ID and pre or post measurement from the column name
            participant_id = re.search(r'P\d{3}', col).group()
            pre_post = re.search(r'(pre|post)', col).group()
            # Extrahiere die relevanten Informationen
            owner = re.sub(r'\.\d+$', '', col)
            location = self.raw_data.iloc[0, col_index]  # 'location' (Gelenk) ist in Zeile 2

            # Füge die Daten Zeile für Zeile hinzu
            for cycle, value in zip(cycle_data, experiment_data):
                data_list.append({
                    'experiment': self.experiment_type,
                    'owner': owner,
                    'source': self.measurement_source,
                    'bpm': 50,
                    'stroke_nr': i,
                    'participant_id': participant_id,
                    'pre_post': pre_post,
                    'axis':axis,
                    'location': location,
                    'time_index': int(cycle),
                    'data': float(value)
                })

        # Erstellen des neuen DataFrames
        self.processed_data = pd.DataFrame(data_list)
        # Create the new column based on the conditions
        # TODO: check how to split between up and downstroke (if possible)
        self.processed_data['bow_stroke'] = self.processed_data['stroke_nr'].apply(lambda x: "BOWING_DOWN" if x%2 == 0 else 'BOWING_UP')
        self.processed_data['cycle_index'] = self.processed_data['time_index']
        #self.processed_data['bow_stroke'] = self.processed_data['cycle_index'].apply(lambda x: "BOWING_UP" if x <= 50 else 'BOWING_DOWN')
        #self.processed_data['time_index'] = self.processed_data['cycle_index'].apply(lambda x: x if x <= 50 else x-50)
        


        return self.processed_data

    #def extract_data_points(self, data_str, num_points=51):
    #    """Extract numerical data points from a string (e.g. '85.273,85.246,...')."""
    #    data_points = [float(x) for x in data_str.split(',')]
    #    if len(data_points) != num_points:
    #        raise ValueError(f"Expected {num_points} data points, but got {len(data_points)}.")
    #    return data_points

    #def standardize_columns(self):
    #    """Rename columns based on the provided column mappings."""
    #    if self.column_mappings:
    #        self.data = self.data.rename(columns=self.column_mappings)
    #    return self.data
#
    #def clean_data(self):
    #    """Perform data cleaning tasks such as handling missing values."""
    #    # Example: Drop rows with missing values
    #    self.data = self.data.dropna()
    #    # Additional cleaning operations can be added here
    #    return self.data
#
    #def process(self):
    #    """Run the full processing pipeline."""
    #    self.standardize_columns()
    #    self.clean_data()
    #    return self.data

# TEMP
# used to test the script
from file_handler import *
from pathlib import Path

def main():
    
    
    # Get the path of the current script
    current_path = Path(__file__).resolve().parent

    # Navigate to the parent folder
    parent_path = current_path.parent

    # TODO include information about EMG or Motion Cap
    # Construct the path to the data folder
    filepath_xml = parent_path / 'Sample_Data_PAH/RefLabPerform/export/joints/23_R_ELBOW_JOINT.xml'
    filepath_tsv = parent_path / 'Sample_Data_PAH/MusikPhysioAnalysis/00_VIOLIN/00_JOINT_ANGLE/RIGHT_ELBOW_JOINT_ANGLE_Z.tsv'

    # Create Filehandler
    filehandler_xml = FileHandler(filepath_xml)
    filehandler_tsv = FileHandler(filepath_tsv)

    filehandler_xml.load_file()
    filehandler_tsv.load_file()

    data_processed_xml = DataProcessor(filehandler_xml.data, 'ref_lab', 'motion_capture')
    data_processed_tsv = DataProcessor(filehandler_tsv.data, 'mpa', 'motion_capture')

    data_processed_xml.process()
    data_processed_tsv.process()

    data_combined = pd.concat([data_processed_xml.processed_data, data_processed_tsv.processed_data], ignore_index=True)
    data_combined.head()
    print('')


if __name__ == "__main__":
    main()