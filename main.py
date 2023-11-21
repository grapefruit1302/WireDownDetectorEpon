from easysnmp import Session
import struct
import time 
import configparser

class WireDownDetectorEpon:
    def __init__(self, olt_ip, community_string="public"):
        self.olt_ip = olt_ip
        self.community_string = community_string
        self.session = Session(hostname=self.olt_ip, community=self.community_string, version=2)
        self.deregistration_info = {}
        self.branch_info = {}

    def ont_dereg_reason_code(self, code):
        status_mapping = {
            "0": "unknown",
            "2": "normal",
            "3": "mpcp-down",
            "4": "oam-down",
            "5": "firmware-download",
            "6": "illegal-mac",
            "7": "admin-down",
            "8": "wire-down",
            "9": "power-off"
        }
        return status_mapping.get(code)

    def check_branch_code(self, code):
        status_mapping = {
            47: "1 гілка",
            48: "2 гілка",
            49: "3 гілка",
            50: "4 гілка",
            51: "5 гілка",
            52: "6 гілка",
            53: "7 гілка",
            54: "8 гілка",
            55: "9 гілка",
            56: "10 гілка",
            57: "11 гілка",
            58: "12 гілка",
            59: "13 гілка",
            60: "14 гілка",
            61: "15 гілка",
            62: "16 гілка"
        }
        return status_mapping.get(code)

    def process_ont(self, reg_oid, index):
        branch_number = int(reg_oid.oid.split('.')[-7])
        ont_oid = reg_oid.oid.split('.')[-1]

        registration_variable = self.session.get(reg_oid.oid)
        registration_value = registration_variable.value
        registration_time = [ord(char) for char in registration_value]
        reg_year, reg_month, reg_day, reg_hour, reg_minute, reg_second = struct.unpack('>HBBBBB', bytes(registration_time[0:7]))

        deregistration_variable = self.session.get(self.deregistration_times[index].oid)
        deregistration_value = deregistration_variable.value
        deregistration_time = [ord(char) for char in deregistration_value]
        dereg_year, dereg_month, dereg_day, dereg_hour, dereg_minute, dereg_second = struct.unpack('>HBBBBB', bytes(deregistration_time[0:7]))

        dereg_reason_variable = self.session.get(self.deregistration_reasons[index].oid)
        dereg_reason_value = dereg_reason_variable.value

        if (
            reg_year > dereg_year or
            (reg_year == dereg_year and reg_month > dereg_month) or
            (reg_year == dereg_year and reg_month == dereg_month and reg_day > dereg_day) or
            (reg_year == dereg_year and reg_month == dereg_month and reg_day == dereg_day and reg_hour > dereg_hour) or
            (reg_year == dereg_year and reg_month == dereg_month and reg_day == dereg_day and reg_hour == dereg_hour and reg_minute > dereg_minute) or
            (reg_year == dereg_year and reg_month == dereg_month and reg_day == dereg_day and reg_hour == dereg_hour and reg_minute == dereg_minute and reg_second > dereg_second)
        ):
            ont_status = "active"
        else:
            ont_status = "deregistered"

            if int(dereg_reason_value) == 8:
                dereg_time = (dereg_year, dereg_month, dereg_day, dereg_hour, dereg_minute, dereg_second)
                branch_number = int(reg_oid.oid.split('.')[-7])
                self.deregistration_info.setdefault(dereg_time, {"count": 0, "registered_onus": [], "branch": branch_number})
                self.deregistration_info[dereg_time]["count"] += 1
                self.deregistration_info[dereg_time]["registered_onus"].append(ont_oid)

        self.branch_info.setdefault(branch_number, {"count": 0, "registered_onus": []})
        self.branch_info[branch_number]["count"] += 1
        self.branch_info[branch_number]["registered_onus"].append(ont_oid)

        # print(f"ONT OID: {ont_oid}")
        # print(f"  Status: {ont_status}")
        # print(f"  Deregistration Reason: {self.ont_dereg_reason_code(dereg_reason_value)}")
        # print(f"  Registration Time: {reg_year}-{reg_month:02d}-{reg_day:02d} {reg_hour:02d}:{reg_minute:02d}:{reg_second:02d}")
        # print(f"  Deregistration Time: {dereg_year}-{dereg_month:02d}-{dereg_day:02d} {dereg_hour:02d}:{dereg_minute:02d}:{dereg_second:02d}")
        # print(f"  Branch Number: {self.check_branch_code(branch_number)}")
        # print("=" * 40)

    def process_branch_info(self):
        for branch_number, info in self.branch_info.items():
            print(f"Branch Number: {self.check_branch_code(branch_number)}")
            print(f"  Number of Registered ONUs: {info['count']}")
            print(f"  Registered ONUs: {', '.join(info['registered_onus'])}")
            print("=" * 40)

    def process_deregistration_info(self):
        if self.deregistration_info:
            print("розреєстровані ону//")
            print(self.olt_ip)
            for dereg_time, onu_info in self.deregistration_info.items():
                if onu_info["count"] >= 2:
                    print(f"{self.check_branch_code(onu_info['branch'])}// {onu_info['count']} ону//")

    def run(self):
        registration_time_oid = "1.3.6.1.4.1.3320.101.11.1.1.9"
        deregistration_time_oid = "1.3.6.1.4.1.3320.101.11.1.1.10"
        deregistration_reason_oid = "1.3.6.1.4.1.3320.101.11.1.1.11"

        self.registration_times = self.session.walk(registration_time_oid)
        self.deregistration_times = self.session.walk(deregistration_time_oid)
        self.deregistration_reasons = self.session.walk(deregistration_reason_oid)

        for index, reg_oid in enumerate(self.registration_times):
              self.process_ont(reg_oid, index)

        #self.process_branch_info()
        self.process_deregistration_info()


def read_ips_from_file(file_path):
    with open(file_path, 'r') as file:
        ips = file.read().splitlines()
    return ips

def read_config(file_path='config.ini'):
    config = configparser.ConfigParser()
    config.read(file_path)

    try:
        interval_str = config['General'].get('Interval')
        interval = int(''.join(filter(str.isdigit, interval_str)))
        file_path = config['General'].get('FilePath')
    except (KeyError, ValueError):
        print("Error: Invalid or missing values in the configuration file.")
        return None, None

    return interval, file_path

def main():
    interval, file_path = read_config()

    if interval is not None and file_path is not None:
        while True:
            ips = read_ips_from_file(file_path)

            if ips:
                for ip in ips:
                    wireDownDetectorEpon = WireDownDetectorEpon(ip)
                    wireDownDetectorEpon.run()

                print("Waiting for the next batch...")
                time.sleep(interval)
            else:
                print("IP not found")
                break

if __name__ == "__main__":
    main()