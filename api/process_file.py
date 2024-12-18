import os
import json

from .gpt_api_handler import chat_with_gpt
from .google_api_handler import google_search
import sys
sys.stdout.reconfigure(encoding='utf-8')  # Set the standard output encoding to UTF-8
import csv

CSV_PATH = 'results.csv'



"""
Main Function. Reads data from Export.json and writes domain data onto the csv file
"""
def process(json_file):
    dataset = []
    csv_header = ["Company Name", "EV Charger Location", "Domain"]
 
    
    # try:
    #     with open('export.json', 'r') as file:

    previous_data = {"address" : None}

    # loop counter for TESTING 
    counter = 0

    # Iterate through each line in the export.json file
    for data in json_file:
        print(data)
        # Turn the line to a dictionary
        # data = json.loads(line) 
        # find_company_name = read_file_to_string("find_company_name.txt")
        # find_domain = read_file_to_string("find_domain.txt")
        find_company_name = "You are an assistant tasked with identifying the company or organization associated with a specific address based on search results. The address might represent a commercial, retail, or public venue. Use contextual and public knowledge to determine the most relevant company or organization. Search results will often mention the name of the company tied to the address. Respond with only the company's name or 'Unknown' if no clear association exists."
        find_domain = "Look through the search results to see if the official company domain is listed. Official domain: The domain will often have the company name in the URL (e.g., www.companyname.com). Avoid real estate websites (e.g., Apartments.com, Zillow) as they are not the official company websites. Companies of interest include property management companies, condo management companies, loft management companies, Facility management companies, Building management companies. Return the Domain: If the official domain is found in the search results, return WITH ONLY the domain and NOTHING ELSE. If no domain is found, return 'Unknown Domain'."
        
        print(find_company_name)
        print(find_domain)

        # Make sure the address and location is different. THIS ASSUMES THAT THE LIST IS ALREADY SORTED!!!
        if data["address"] != previous_data["address"]:   
                
            ''' FIRST METHOD : CHROME WEBSEARCH AND CHATGPT '''
            # Create the address of the location
            # Search the address with Google Search API
            # Inquire ChatGPT and determine owner based on websearch results
            # Search {owner} + Official Website with Google Search API
            # Inquire ChatGPT and determine company domain
        
            if data.get('city','NA') != 'NA':
                address = f"{data['city']} {data.get('address', 'Unknown Address')}"
            else:
                address = f"{data.get('address', 'Unknown Address')}"

            google_search_results = google_search(address,6)
            owner = chat_with_gpt(find_company_name, google_search_results)

            if (owner.lower() != "unknown"):
                query = f"{owner} {data.get('city', data.get('postalcode', '')) if data.get('city', '') != 'NA' else data.get('postalcode', '')} Official Website"
                print(query)
                google_search_results = google_search(query, 6)

                print(f"GOOGLE SEARCH RESULT: {google_search_results}")

                domain = chat_with_gpt(find_domain, google_search_results)
                
                line = {"Company Name":owner, "Address": address, "Domain": domain}
                dataset.append(line)
                
            # Saving the current dictionary that holds data to previous data. 
            previous_data = data
        
        # USED FOR TESTING
        counter += 1
        print(f"{counter} {owner}")
        # if counter > 5: break

    return dataset


    # WRITING ONTO RESULTS.CSV
    # write_dict_to_csv(CSV_PATH, dataset)


    
    # USED FOR TESTING Printing Owner
    for data in dataset:
        print(data)
        print()


                    

    # except FileNotFoundError:
    #     print("File not found.")
    # except json.JSONDecodeError:
    #     print("Invalid JSON format.")



def read_file_to_string(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

# Write the list of dictionaries to the CSV file
def write_dict_to_csv(path, data):

    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, mode='w', newline='') as file:
        # Get the fieldnames from the first dictionary
        fieldnames = data[0].keys()        
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
