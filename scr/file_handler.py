import pandas as pd
from lxml import etree

class FileHandler:
    def __init__(self, file_path):
        """
        Initialize the FileHandler for a filepath.

        Parameters:
        - file_path: The path to the file that should be loaded.
        """
        self.file_path = file_path
        self.data = None

    def parse_data(self, data_str):
        """convert comma-separated string to list of floats"""
        if data_str:
            return [float(x) for x in data_str.split(',')]
        return []
    
    def load_file(self):
        """Identify file format and call respective loader method"""
        if str(self.file_path).endswith('.csv'):
            self.data = self._load_csv()
        elif str(self.file_path).endswith('.tsv'):
            self.data = self._load_tsv()
        elif str(self.file_path).endswith('.xml'):
            self.data = self._load_xml()
        elif str(self.file_path).endswith('.xlsx'):
            self.data = self._load_excel()
        # Add more formats as needed
        return self.data

    def _load_csv(self):
        """Load CSV file logic"""
        return pd.read_csv(self.file_path)
    
    def _load_tsv(self):
        """Load TSV file logic"""
        return pd.read_csv(self.file_path, delimiter='\t')

    def _load_xml(self):
        """Parse XML file"""
        tree = etree.parse(self.file_path)
        root = tree.getroot()

        # List to store data for DataFrame
        data = []

        # Iterate over each 'owner' element
        for owner in root.findall('owner'):
            owner_value = owner.get('value')

            # Iterate over each 'type' element
            for type_element in owner.findall('type'):
                type_value = type_element.get('value')

                # Iterate over each 'folder' element
                for folder in type_element.findall('folder'):
                    folder_value = folder.get('value')

                    # Iterate over each 'name' element
                    for name in folder.findall('name'):
                        name_value = name.get('value')

                        # Iterate over each 'component' element
                        for component in name.findall('component'):
                            component_value = component.get('value')
                            event_sequence = component.get('Event_Sequence')
                            frame_start = int(component.get('Frame_Start', 0))
                            frame_end = int(component.get('Frame_End', 0))
                            time_start = float(component.get('Time_Start', 0.0))
                            time_end = float(component.get('Time_End', 0.0))
                            frames = int(component.get('frames', 0))
                            data_str = component.get('data')

                            # Convert 'data' to a list of floats
                            data_list = self.parse_data(data_str)

                            # Append the data to the list
                            data.append({
                                'owner': owner_value,
                                'type': type_value,
                                'folder': folder_value,
                                'name': name_value,
                                'component_value': component_value,
                                'event_sequence': event_sequence,
                                'frame_start': frame_start,
                                'frame_end': frame_end,
                                'time_start': time_start,
                                'time_end': time_end,
                                'frames': frames,
                                'data': data_list
                            })

        # Create DataFrame from the data list
        df = pd.DataFrame(data)

        return df

    def _load_excel(self) -> pd.DataFrame:
        """Load Excel file logic"""
        if self.excel_sheet_name == None:
            return pd.read_excel(self.file_path)
        else:
            return pd.read_excel(self.file_path, sheet_name=self.excel_sheet_name)
    


# TEMP
# used to test the script
def main():
    from pathlib import Path
    # Get the path of the current script
    current_path = Path(__file__).resolve().parent

    # Navigate to the parent folder
    parent_path = current_path.parent

    # Construct the path to the data folder
    #filepath_xml = parent_path / 'Sample_Data_PAH/RefLabPerform/export/joints/23_R_ELBOW_JOINT.xml'
    filepath_tsv = parent_path / 'Sample_Data_PAH/MusikPhysioAnalysis/00_VIOLIN/00_JOINT_ANGLE/output/RIGHT_ELBOW_JOINT_ANGLE_Z.tsv'

    # Create Filehandler
    #filehandler_xml = FileHandler(filepath_xml)
    filehandler_tsv = FileHandler(filepath_tsv)

    #filehandler_xml.load_file()
    filehandler_tsv.load_file()

    print('')


if __name__ == "__main__":
    main()