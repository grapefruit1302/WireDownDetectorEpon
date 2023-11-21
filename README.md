
# WireDownDetectorEpon
WireDownDetectorEpon is a Python script designed for detecting wire down events and monitoring the status of Optical Network Terminals (ONTs) on an EPON (Ethernet Passive Optical Network) device.

# Features
Wire Down Detection: Monitors and identifies instances where the optical network wire is disconnected, leading to ONT deregistrations.

ONT Status Monitoring: Provides real-time information about the registration and deregistration status of ONTs on EPON devices.

Registration and Deregistration Details: Offers detailed information about the registration time, deregistration time, and the reason for deregistration.

Branch-wise Statistics: Tracks the count of registered ONUs (Optical Network Units) for each branch, aiding in localized issue identification.

Deregistration Log: Identifies and logs ONUs that have been deregistered more than once, indicating potential wire down incidents.

# Requirements
Python 3.x
easysnmp
configparser
