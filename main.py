# main.py

def main():
    """Interactive entrypoint that uses the Storage, Truck and HelpStation APIs.

    - Government users can add supplies or check inventory.
    - Non-government users can request aid and trucks will be dispatched as needed.
    """
    import json
    import sys
    sys.path.append('src')  # Add src directory to Python path
    from storage import Storage
    from trucks import Truck
    from help_stations import HelpStation
    from report_utils import geocode
    # mental health module (optional)
    try:
        import mental_health_ai
    except Exception:
        mental_health_ai = None
    from typing import List, Dict, Tuple, Optional
    import re
    import subprocess
    import importlib

    print("Welcome to the Aid Dispatch System")

    # Define available supply categories and their units
    SUPPLY_CATEGORIES: Dict[str, str] = {
        'food': 'lbs',
        'medical': None,  # no units, just availability
        'blankets': 'quantity',
        'water': 'lbs'
    }

    def format_supply_name(name: str, quantity: int, unit: str) -> str:
        """Format a supply name with its quantity and unit."""
        if unit is None:
            return name
        return f"{name} ({quantity} {unit})"

    def get_supply_choices() -> List[Tuple[str, str]]:
        """Return list of (name, unit) tuples for supplies."""
        return [(name, unit or '') for name, unit in SUPPLY_CATEGORIES.items()]

    # Use persistent storage so supplies survive program restarts
    storage = Storage('data/storage.json')
    trucks = Truck()
    help_stations = HelpStation()

    # Seed some trucks
    for i in range(1, 6):
        trucks.add_truck(f"Truck {i}")


    # Authentication flow: ask for gov password; blank or incorrect => non-gov
    GOV_PASSWORD = 'gov'
    pwd = input("Enter gov password (leave blank if non-government): ").strip()

    if pwd == GOV_PASSWORD:
        while True:
            action = input("Enter 'add' to add supplies, 'check' inventory, 'reports' to manage reports, 'stations' to manage aid centres, or 'exit': ").strip().lower()
            if action == 'stations':
                while True:
                    print("\nAid Centre Management")
                    print("1. Add new aid centre")
                    print("2. List aid centres")
                    print("3. Delete aid centre")
                    print("4. Back to main menu")
                    
                    choice = input("Enter choice (1-4): ").strip()
                    if choice == '1':
                        name = input("Enter aid centre name: ").strip()
                        if help_stations.add_station(name):
                            print(f"Added aid centre: {name}")
                        else:
                            print("Failed to add station - name empty or already exists")
                    
                    elif choice == '2':
                        all_stations = help_stations.list_stations()
                        if all_stations:
                            print("\nRegistered Aid Centres:")
                            for station in all_stations:
                                print(f" - {station}")
                        else:
                            print("No aid centres registered.")
                    
                    elif choice == '3':
                        name = input("Enter aid centre name to delete: ").strip()
                        if help_stations.delete_station(name):
                            print(f"Deleted aid centre: {name}")
                        else:
                            print("Station not found")
                            
                    elif choice == '4':
                        break
                    else:
                        print("Invalid choice. Please try again.")
                continue
                
            elif action == 'add':
                # Show available categories
                print("\nAvailable supply categories:")
                for i, (name, unit) in enumerate(get_supply_choices(), 1):
                    print(f"{i}. {name}" + (f" (measured in {unit})" if unit else ""))
                
                try:
                    choice = int(input("\nEnter category number (1-4): ").strip())
                    if not (1 <= choice <= 4):
                        raise ValueError("Invalid choice")
                    supply = list(SUPPLY_CATEGORIES.keys())[choice - 1].lower()
                except (ValueError, IndexError):
                    print("Invalid choice. Please enter a number between 1 and 4.")
                    continue

                if supply == 'medical':
                    # Medical supplies are tracked as available/unavailable (1/0)
                    storage.add_supplies(supply, 1)
                    print(f"Added medical supplies to storage.")
                    continue

                try:
                    unit = SUPPLY_CATEGORIES[supply]
                    quantity = int(input(f"Enter quantity ({unit}): ").strip())
                    if quantity <= 0:
                        raise ValueError("Quantity must be positive")
                except ValueError:
                    print("Invalid quantity. Please enter a number.")
                    continue

                storage.add_supplies(supply, quantity)
                print(f"Added {format_supply_name(supply, quantity, unit)} to storage.")
            elif action == 'reports':
                while True:
                    print("\nDisaster Reports Management")
                    print("1. View reports")
                    print("2. Delete report")
                    print("3. Back to main menu")
                    
                    choice = input("Enter choice (1-3): ").strip()
                    if choice == '1':
                        reports = storage.get_reports()
                        if not reports:
                            print("No reports available.")
                        else:
                            print("\nSaved disaster reports:")
                            for i, r in enumerate(reports, start=1):
                                # Show reporter, type, parsed details, resolved address and coordinates if available
                                name = r.get('name', 'Unknown')
                                dtype = r.get('disaster_type', 'Unknown')
                                details_raw = r.get('details', '') or ''

                                def _extract_location_from_details(details: str) -> Tuple[Optional[str], Optional[float], Optional[float]]:
                                    if not details:
                                        return None, None, None
                                    addr = None
                                    lat = None
                                    lon = None
                                    if "location_resolved:" in details:
                                        try:
                                            addr_part = details.split("location_resolved:", 1)[1]
                                            addr = addr_part.split("|", 1)[0].strip()
                                            if addr == "":
                                                addr = None
                                        except Exception:
                                            addr = None
                                    mlat = re.search(r"lat:\s*([\-\d\.]+)", details)
                                    mlon = re.search(r"lon:\s*([\-\d\.]+)", details)
                                    try:
                                        if mlat:
                                            lat = float(mlat.group(1))
                                    except Exception:
                                        lat = None
                                    try:
                                        if mlon:
                                            lon = float(mlon.group(1))
                                    except Exception:
                                        lon = None
                                    return addr, lat, lon

                                def _extract_description_from_details(details: str) -> str:
                                    if not details:
                                        return ""
                                    if "location_resolved:" in details:
                                        return details.split("location_resolved:", 1)[0].rstrip(" |").strip()
                                    return details.strip()

                                description = _extract_description_from_details(details_raw)
                                addr, lat, lon = _extract_location_from_details(details_raw)
                                addr_display = addr or 'Address unknown'
                                lat_display = lat if lat is not None else 'N/A'
                                lon_display = lon if lon is not None else 'N/A'

                                print(f"{i}. Reporter: {name}")
                                print(f"   Type   : {dtype}")
                                print(f"   Details: {description}")
                                print(f"   Address: {addr_display}")
                                print(f"   Lat/Lon: {lat_display} / {lon_display}")
                                print('-' * 60)
                    
                    elif choice == '2':
                        reports = storage.get_reports()
                        if not reports:
                            print("No reports available to delete.")
                            continue
                            
                        print("\nCurrent reports:")
                        for i, r in enumerate(reports, start=1):
                            print(f"{i}. {r.get('timestamp')} - {r.get('name')} - {r.get('disaster_type')}")
                        
                        try:
                            index = int(input("\nEnter report number to delete (0 to cancel): ").strip())
                            if index == 0:
                                continue
                            if storage.delete_report(index):
                                print("Report deleted successfully.")
                            else:
                                print("Invalid report number.")
                        except ValueError:
                            print("Invalid input. Please enter a number.")
                    
                    elif choice == '3':
                        break
                    else:
                        print("Invalid choice. Please try again.")
                continue
            elif action == 'check':
                supplies = storage.get_supplies()
                if not supplies:
                    print("No supplies in storage.")
                else:
                    print("\nCurrent supplies in storage:")
                    for supply, quantity in supplies.items():
                        # Convert to lowercase for comparison
                        supply_lower = supply.lower()
                        # Find matching category if any
                        category = next((cat for cat in SUPPLY_CATEGORIES.keys() if cat.lower() == supply_lower), None)
                        
                        if supply_lower == 'medical':
                            status = "Available" if quantity > 0 else "Not available"
                            print(f"Medical supplies: {status}")
                        elif category:
                            unit = SUPPLY_CATEGORIES[category]
                            print(f"{format_supply_name(category, quantity, unit)}")
                        else:
                            # Handle legacy or unknown supplies
                            print(f"{supply}: {quantity}")
            elif action == 'exit':
                break
            else:
                print("Invalid action. Please try again.")

    else:
        # Non-government flow: require the requester to confirm 'non' and state their name
        confirm = input("Enter 'non' to continue as non-government (or anything else to exit): ").strip().lower()
        if confirm != 'non':
            print("Exiting.")
            return

        user_name = input("Enter your name: ").strip()
        if not user_name:
            user_name = "Requester"

        # persist requester name so it's available after program restarts
        storage.add_requester(user_name)

        # Prompt to file a disaster report
        report_choice = input("Would you like to file a disaster report? (y/n): ").strip().lower()
        if report_choice == 'y':
            disaster_type = input("Type of natural disaster (e.g., flood, earthquake): ").strip()
            details = input("Please provide brief details about the situation: ").strip()

            # Ask for address components and attempt geocoding (same behaviour as data analysis report)
            print("\nPlease provide the location for this report (leave blank if unknown).")
            number = input("Address (number) : ").strip()
            street = input("Street name      : ").strip()
            city = input("City / Town      : ").strip()
            country = input("Country          : ").strip()

            coords = geocode(number or None, street, city, country)
            if coords is None:
                storage.add_report(user_name, disaster_type, details)
                print("Thank you — your report has been saved and will be visible to government users.")
            else:
                lat, lon, display = coords
                details_with_location = f"{details} | location_resolved: {display} | lat:{lat} lon:{lon}"
                storage.add_report(user_name, disaster_type, details_with_location)
                print("Thank you — your report has been saved (address resolved) and will be visible to government users.")

        # For non-government users: do not ask for latitude/longitude.
        # Always attempt to dispatch a truck when supplies are available.
        while True:
            action = input("Enter 'request' to request aid, 'mental' for mental health support, 'stations' to list stations, or 'exit' to quit: ").strip().lower()
            if action == 'request':
                # Show available supplies
                print("\nAvailable supplies:")
                supplies = storage.get_supplies()
                available_supplies = []
                
                for supply, quantity in supplies.items():
                    supply_lower = supply.lower()
                    category = next((cat for cat in SUPPLY_CATEGORIES.keys() if cat.lower() == supply_lower), None)
                    
                    if category:
                        unit = SUPPLY_CATEGORIES[category]
                        if supply_lower == 'medical' and quantity > 0:
                            print(f"{len(available_supplies) + 1}. Medical supplies (Available)")
                            available_supplies.append(('medical', None))
                        elif quantity > 0:
                            print(f"{len(available_supplies) + 1}. {category} ({quantity} {unit} available)")
                            available_supplies.append((category, unit))
                
                if not available_supplies:
                    print("Sorry, no supplies are currently available.")
                    continue
                
                try:
                    choice = int(input("\nEnter supply number (or 0 to cancel): ").strip())
                    if choice == 0:
                        continue
                    if not (1 <= choice <= len(available_supplies)):
                        print("Invalid choice.")
                        continue
                        
                    supply, unit = available_supplies[choice - 1]
                    max_available = storage.check_inventory(supply)
                    
                    # Handle quantity request
                    if supply == 'medical':
                        quantity = 1
                    else:
                        print(f"\nAvailable {supply}: {max_available} {unit}")
                        try:
                            quantity = int(input(f"Enter amount needed (1-{max_available}): ").strip())
                            if quantity <= 0 or quantity > max_available:
                                print(f"Invalid amount. Please enter a number between 1 and {max_available}.")
                                continue
                        except ValueError:
                            print("Invalid input. Please enter a number.")
                            continue
                    
                    # Find available truck
                    available_truck = None
                    for name, available in trucks.trucks.items():
                        if available:
                            available_truck = name
                            break

                    if available_truck:
                        trucks.dispatch_truck(available_truck)
                        try:
                            # Double check the current inventory before removing
                            current_quantity = storage.check_inventory(supply)
                            if quantity > current_quantity:
                                print(f"Sorry, only {current_quantity} {unit} of {supply} available now.")
                                continue
                                
                            storage.remove_supplies(supply, quantity)
                            if supply == 'medical':
                                print(f"{available_truck} has been dispatched with medical supplies to {user_name}'s location.")
                            else:
                                print(f"{available_truck} has been dispatched with {quantity} {unit} of {supply} to {user_name}'s location.")
                        except ValueError as e:
                            print(f"Error: {str(e)}")
                            continue
                    else:
                        print("No trucks available to dispatch at the moment.")
                    
                    # Ask if they want to request more
                    more = input("\nWould you like to request more supplies? (y/n): ").strip().lower()
                    if more != 'y':
                        action = 'exit'  # This will break the main loop
                        
                except ValueError:
                    print("Invalid input. Please try again.")

            elif action == 'stations':
                all_stations = help_stations.list_stations()
                if all_stations:
                    print("\nKnown help stations:")
                    for station in all_stations:
                        print(f" - {station}")
                else:
                    print("No help stations registered.")

            elif action == 'mental':
                if mental_health_ai is None:
                    print("Mental health support is unavailable: missing module or dependencies.")
                    print("Run the setup script or install requirements to enable it.")
                    continue

                # If not configured, prompt user to provide API key
                try:
                    configured = False
                    if hasattr(mental_health_ai, 'is_configured'):
                        configured = mental_health_ai.is_configured()
                    else:
                        configured = getattr(mental_health_ai, 'client', None) is not None
                except Exception:
                    configured = False

                if not configured:
                    # Prompt user for API key once, then automatically persist to local .env
                    key = input("Mental health AI is not configured. Enter your OpenAI API key (or leave blank to cancel): ").strip()
                    if not key:
                        print("No key entered — returning to menu.")
                        continue
                    try:
                        # Automatically set session env var and write a local .env (gitignored)
                        ok = mental_health_ai.set_api_key(key, persist_env=True, write_dotenv=True)
                        if ok:
                            print("Mental health AI configured successfully.")
                            configured = True
                        else:
                            # If OpenAI SDK was missing in the environment, attempt to install it automatically and retry once.
                            openai_present = getattr(mental_health_ai, 'OpenAI', None) is not None
                            if not openai_present:
                                print("OpenAI package not detected. Attempting to install 'openai' now (this may take a minute)...")
                                try:
                                    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"]) 
                                    # Reload the mental_health_ai module so it picks up the newly installed package
                                    importlib.reload(mental_health_ai)
                                    ok2 = mental_health_ai.set_api_key(key, persist_env=True, write_dotenv=True)
                                    if ok2:
                                        print("Installed OpenAI and configured mental health AI successfully.")
                                        configured = True
                                    else:
                                        print("Installed 'openai' but failed to initialize client. Check API key and network access.")
                                        continue
                                except Exception as ie:
                                    print("Automatic installation of 'openai' failed:", repr(ie))
                                    print("Please install requirements manually: python -m pip install -r requirements.txt")
                                    continue
                            else:
                                print("Failed to initialize AI client. Check the key, ensure 'openai' package is installed, and verify network access.")
                                continue
                    except Exception as e:
                        print("Error configuring mental health AI:", repr(e))
                        print("Ensure the 'openai' package is installed and your API key is valid.")
                        continue

                # Present mental health submenu
                while True:
                    print("\nMental Health Support")
                    print("1. Quick message (one-off)")
                    print("2. Full interactive companion")
                    print("3. Back")
                    mh_choice = input("Choose (1-3): ").strip()
                    if mh_choice == '1':
                        user_msg = input("Enter a short message (blank to cancel): ").strip()
                        if not user_msg:
                            continue
                        try:
                            reply = mental_health_ai.update_memory_with_gpt(user_msg)
                        except Exception:
                            reply = "Mental health support is temporarily unavailable."
                        print(f"\nSupport: {reply}\n")
                        try:
                            storage.add_report(user_name, 'mental_support', f"user: {user_msg} | response: {reply}")
                        except Exception:
                            pass
                    elif mh_choice == '2':
                        try:
                            mental_health_ai.main()
                        except Exception as e:
                            print("Mental health companion failed:", e)
                    elif mh_choice == '3':
                        break
                    else:
                        print("Invalid choice. Please enter 1, 2 or 3.")

            elif action == 'exit':
                break
            else:
                print("Invalid action. Please try again.")
    

if __name__ == "__main__":
    main()