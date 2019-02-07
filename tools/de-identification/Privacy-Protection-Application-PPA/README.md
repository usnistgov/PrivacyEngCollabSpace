# Privacy Protection Application (PPA)          

**Brief Description:** The Privacy Protection Application de-identifies databases that contain sequential geolocation data, sometimes called moving object databases. A record of a personally-owned vehicle’s route of travel is an example, but the tool can process other types of geolocation sequences. The application has a graphical user interface and operates on Linux, OS X, and Windows. Location suppression is the de-identification strategy used, and decisions about which locations to suppress are based on information theory. This strategy does not modify the precision of retained location information. One of the objectives is to produce data usable for vehicle safety analysis and transportation application development. 

**Link to Tool:** [https://github.com/usdot-its-jpo-data-portal/privacy-protection-application](https://github.com/usdot-its-jpo-data-portal/privacy-protection-application) 

**Primary Tool Focus Area:** De-identification

**Keywords:** K-Anonymity, Anonymization, Information Leakage, Algorithmic Fairness, Database Queries, Location Data

**Email POC:** carterjm@ornl.gov 

**Additional Notes:** This tool treats static databases and has two versions.  The main GUI versions uses a very efficient map matching strategy that may identify false roads for certain types of road structures.  The tagged version ([https://github.com/usdot-its-jpo-data-portal/privacy-protection-application/releases/tag/hmm-mm]()) uses a Hidden Markov Model map matching algorithm that is more accurate, but less efficient. This version is a command line tool that runs in Docker. Additionally, a streaming de-identification tool was developed for a USDOT Safety Pilot Study. This tool uses geofencing to identify locations that can be retained. It can also be found on GitHub: [https://github.com/usdot-jpo-ode/jpo-cvdp]()
