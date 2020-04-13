# tele-triage
Details on what is Sequoia, the problem it tackles, how to use Sequoia, and next steps

# Summary
Sequoia is an SMS-based platform made to help hospitals handle the burden of exponential patient influx by remotely connecting users to healthcare providers for triage

# Navigating this repo
* deliverables: writeup, slides, and video demo
* // TODO - list folders, summarize contents

# How to use Sequoia
User: Text HELLO to 618-643-9906

Provider: After a user submits a triage request, triage users here: http://159.89.236.70/

# Problem overview
The healthcare system is being overwhelmed by an exponential patient influx at clinical entry points during the COVID-19 pandemic. Research from the CDC, NCBI, and UpToDate states that clinical presentation of COVID-19 can vary greatly in clinical manifestations and disease severity, indicating that different patients are best treated at different care facilities (Trauma level 1, Trauma level 2, Trauma level 3, etc.) that best fit their needs. There is a need to get the right patients to the right facilities at the right times to avoid a massive influx that will create hospital backlogs that will needlessly overburden health care facilities, divert valuable time away from in-person care, and hasten the spread of COVID-19.

# Problem in action
* 41 states are predicted to have insufficient ICU beds (11 of which are expected to require a >50% boost in capacity) to handle the upcoming COVID-19 patient influx.
* Meta-analysis of pure machine-based "symptom checkers" indicates that such machine-based tools exhibit their greatest failure rates in the context of triage. The best tools studied demonstrated a 78% accuracy in triage advice - with others as low as 33%.
* A 2019 survey of students in Boston and New York showed a 53% greater adherence rate for care suggestions when medical information was provided by a human in comparison to a solely AI-based tool.

Summary: This problem is time-sensitive and is expected to impact the U.S. soon. Machine-based triage systems are less effective than a physician- or human-driven triage solution.

# Solution
Sequoia is an SMS-based platform based on simplicity and flexibility that connects users to a list of appropriate care facilities by utilizing remote provider input.

INPUT FROM USER: Sequoia gathers the user’s responses to automated questions regarding zip code and COVID-19 symptoms into a request, which is placed onto a queue.

INPUT FROM PROVIDER: Authorized healthcare providers (including any provider able to do basic triage) can log on to a web interface to view each queued request. Using their clinical judgement, providers select from a list of care facilities categories (trauma level 1, trauma level 2, trauma level 3, etc.) or options to direct the patient to stay at home, or go to a testing center.

OUTPUT TO USER: Sequoia’s matching algorithm takes in the provider’s selection alongside data on care facility location and available resources to deliver a list of best-fit facilities near the patient via SMS.

# Solution viability
Availability and simplicity to users and providers
* Sequoia allows for crowdsourcing of available healthcare providers during crisis, which allows full utilization of the changing population of available providers. Not limited to only physicians, Sequoia's provider base could include nurses, physician assistants, residents, fourth-year medical students, retired physicians, and other allied health professionals.
* Sequoia is easily accessible by users. Anyone in need of guidance on whether to get in-person care (and if so, where to receive care) can text Sequoia's hotline number and receive a response through SMS.
* Sequoia is designed to integrate seamlessly into a provider's workflow. Certified providers can simply log on to Sequoia's web interface, view a patient request from the queue, and choose a triage level. This simplicity removes the need for in-depth training on how to navigate the web interface.

Speed and flexibility
* Sequoia works with great speed. Discussions with providers gave us an estimate that fulfilling a single patient request would take at most 5 minutes.
* Sequoia accounts for anomalous requests. Only if needed, a provider can contact a user for more information via telephone or teleconference.
* Sequoia is a flexible system. In a climate of changing information, the user questionnaire can be adjusted as more information regarding COVID-19 symptoms becomes available, and providers can adjust their triage decisions as new information comes to light.

# Use cases
Intra-system Use:

Individual health systems can use Sequoia to efficiently direct patients between existing care facilities within a single health system. This would minimize crowding emergency departments or overwhelming phone lines. Even outside a pandemic setting, intra-system use would ameliorate health care conditions during a localized crisis as health providers within a health system can coordinate reduce overloading of a single health care facility during a crisis.

Inter-system Use:

In a situation where a pandemic or other crisis is so severe that individual health systems cannot handle the massive patient influx on their own, multiple health systems using Sequoia's basic framework can connect their platforms and combine their provider bases, lists of care facility options, and available care facility data. This would allow users in need to receive an expanded list of care facilities, and patient influx could be efficiently distributed between multiple health care systems.

# How it's built
* The Sequoia platform utilizes Twilio for programmatic SMS and Flask / waitress for a web server, running on a DigitalOcean droplet. To support large volumes of users, Sequoia uses a queue-based system to match a specific provider with a user to triage, and a secondary producer-consumer thread system for off-main-thread querying of web-based GeoJSON APIs. In addition, Sequoia uses an extensible and adaptable weighting system to match each user with a health care center, based on available resources, distance, and care level.
* Data about hospital locations and triage levels come from CMS (Centers for Medicare & Medicaid Services)
* User symptom questionnaire was derived from the Washington University in St. Louis daily self-screening questionnaire for employees.
* // TODO Add relevant technical details here

# Next Steps
Further Design and Testing:

(1) Verification of compliance with HIPAA and PHI standards to receive user information and to allow health providers to legally triage within a single health system and between multiple health systems.

(2) Risk minimization discussions with government and public health agencies. Prior to deployment, we want to de-risk mis-triaging by verifying that the user questionnaire will give providers the necessary information to make an effective triage decision. We will use this information - along with verification of weightings of static factors present in CMS, data from other public databases, and real-time data on resource availability - to refine our matching algorithm that sends a list of appropriate care centers back to the users.

Resources Needed:

(1) Seeking assistance and input from those with legal expertise on electronically transmitting medical information.

(2) Seeking assistance and input from those with government and/or health care agency expertise.

(3) Seeking access to governmental groups outside of Missouri to better understand the scalability of Sequoia on a state-based or national level.

Implementation:
(1) Legal and clinical verification.

(2) Interfacing with two primary players: hospital systems/academic centers and government/public health systems.
     
     (A) Complete a beta-prototype for IRB approval.
     
     (B) Pilot Sequoia in a single locale to test efficacy.
     
     (C) Reach out to county and state municipality public health organizations.

Implementation Notes:
* Projected costs are minimal and only stem from server usage. Sequoia will be provided to users at no cost.
* Sequoia bypasses the need for FDA Class II clearance as a diagnostic by letting a trained, human provider make the triage decision.

# More information
* Devpost page: https://devpost.com/software/sequoia-tgnryh
* COVID-19 Global Hackathon (featured as winning project): https://covidglobalhackathon.com/

# Created by
Undergraduate, graduate, and medical school students at Washington University in St. Louis and Washington University School of Medicine:
* John Gibson (Computer Science)
* Rohit Kumar (Computer Science)
* Ashwin Leo (School of Medicine)
* Kevin Li (Computer Science, Biomedical Engineering)
* Aadit Shah (Biomedical Engineering)
* Lily Xu (Biomedical Engineering, Computational Biology)
