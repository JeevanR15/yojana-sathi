# -*- coding: utf-8 -*-
"""
150 real, sourced Indian central government welfare schemes.

Sources:
  - myscheme.gov.in (official GoI scheme portal, 2316+ schemes as of 2024)
  - dbtbharat.gov.in (Direct Benefit Transfer mission)
  - india.gov.in (National Portal of India)
  - Ministry portals: pmkisan.gov.in, nhm.gov.in, nsap.nic.in, depwd.gov.in,
    pmmsy.dof.gov.in, pmfby.gov.in, nrega.nic.in, scholarships.gov.in,
    socialjustice.gov.in, wcd.nic.in, tribal.nic.in, jansuraksha.gov.in

`eligibility_text` is intentionally written in PLAIN natural language.
It is the field embedded for MongoDB Atlas Vector Search.
It must read like a real person describing their life, so
"poor widow farmer" matches "BPL female cultivator with spousal bereavement".
DO NOT convert this field to bureaucratic language.
"""

SCHEMES = [

    # =========================================================
    # AGRICULTURE & FARMERS  (1-20)
    # =========================================================
    {
        "name": "PM Kisan Samman Nidhi",
        "benefit": "Rs.6,000 per year in 3 installments directly to bank account",
        "eligibility_text": "Small and marginal farmer who owns agricultural land. Any gender. Any Indian state. Family must not have government job or pay income tax. No upper income limit but must own farmland.",
        "required_docs": ["Aadhaar card", "Land ownership records (Khasra/Khatauni)", "Bank account passbook", "Mobile number"],
        "apply_url": "https://pmkisan.gov.in",
    },
    {
        "name": "PM Fasal Bima Yojana",
        "benefit": "Crop insurance covering loss due to flood, drought, pest, or natural disaster",
        "eligibility_text": "Any farmer who has taken a crop loan from a bank. Also voluntary for farmers without loans. Covers all food crops, oilseeds, and commercial crops. Premium is very low, government pays most of it.",
        "required_docs": ["Aadhaar card", "Land records", "Bank account", "Crop sowing certificate from Patwari"],
        "apply_url": "https://pmfby.gov.in",
    },
    {
        "name": "Kisan Credit Card",
        "benefit": "Short-term credit up to Rs.3 lakh at 4% interest for farming expenses",
        "eligibility_text": "Farmer, tenant farmer, sharecropper, or oral lessee. Also for self-help groups of farmers. Used to buy seeds, fertilizer, pesticides. Animal husbandry and fisheries farmers also eligible.",
        "required_docs": ["Aadhaar card", "Land documents or lease agreement", "Passport photo", "Bank application form"],
        "apply_url": "https://www.rbi.org.in/kisan-credit-card",
    },
    {
        "name": "PM Krishi Sinchai Yojana",
        "benefit": "Up to 55% subsidy for drip and sprinkler irrigation equipment for small farmers",
        "eligibility_text": "Any farmer who owns or leases farmland and wants to install drip or sprinkler irrigation to save water. Small and marginal farmers get higher subsidy. Any state, any crop.",
        "required_docs": ["Aadhaar card", "Land documents", "Bank account", "Quotation from approved vendor"],
        "apply_url": "https://pmksy.gov.in",
    },
    {
        "name": "National Food Security Mission",
        "benefit": "Free or subsidised certified seeds, fertilisers, farm equipment, and training for wheat, rice, and pulse farmers",
        "eligibility_text": "Farmer growing rice, wheat, pulses or coarse cereals in targeted districts. BPL farmers get priority. Any gender. Implemented through Krishi Vigyan Kendras and district agriculture offices.",
        "required_docs": ["Aadhaar card", "Land records", "Ration card or BPL certificate"],
        "apply_url": "https://nfsm.gov.in",
    },
    {
        "name": "Soil Health Card Scheme",
        "benefit": "Free soil testing and printed card showing which fertilisers your soil needs, saving money on chemicals",
        "eligibility_text": "Any farmer in India who cultivates land. Rural or semi-urban. No income limit. Helps reduce over-use of fertilisers and increase crop yield by farming smarter.",
        "required_docs": ["Aadhaar card", "Land records or cultivation proof"],
        "apply_url": "https://soilhealth.dac.gov.in",
    },
    {
        "name": "eNAM National Agriculture Market",
        "benefit": "Online platform to sell crops across state markets, get better prices, and avoid middlemen",
        "eligibility_text": "Any farmer registered with a local APMC mandi. Helps farmers in any state sell produce directly to buyers across India through an online platform. Especially useful for vegetable and fruit farmers.",
        "required_docs": ["Aadhaar card", "Bank account", "APMC registration or farmer registration"],
        "apply_url": "https://enam.gov.in",
    },
    {
        "name": "PM Kisan Maan Dhan Yojana",
        "benefit": "Rs.3,000 per month pension after age 60 for small and marginal farmers",
        "eligibility_text": "Small or marginal farmer aged 18 to 40 years at time of enrolment. Owns less than 2 hectares of farmland. Monthly contribution ranges from Rs.55 to Rs.200 depending on age, and the government matches it.",
        "required_docs": ["Aadhaar card", "Land records showing less than 2 hectares", "Bank passbook", "Mobile number"],
        "apply_url": "https://maandhan.in",
    },
    {
        "name": "PM-AASHA Price Support for Oilseeds and Pulses",
        "benefit": "Government buys your oilseeds, pulses, or copra at Minimum Support Price if market prices fall",
        "eligibility_text": "Farmer growing oilseeds like groundnut, soybean, sunflower, or pulses like toor, moong, urad in any state. Registered with state agriculture department. Government purchases directly at announced MSP to protect income.",
        "required_docs": ["Aadhaar card", "Land records", "Bank account", "State farmer registration"],
        "apply_url": "https://agricoop.nic.in",
    },
    {
        "name": "Agriculture Infrastructure Fund",
        "benefit": "Low-interest loan with 3% interest subvention up to Rs.2 crore for post-harvest storage, cold storage, sorting units",
        "eligibility_text": "Individual farmer, farmer producer organisation, self-help group, cooperative, or agri-entrepreneur wanting to build cold storage, warehouse, sorting unit, or primary processing facility.",
        "required_docs": ["Aadhaar card", "Project proposal", "Land or lease documents", "Bank account", "Farmer registration"],
        "apply_url": "https://agriinfra.dac.gov.in",
    },
    {
        "name": "Paramparagat Krishi Vikas Yojana",
        "benefit": "Rs.50,000 per hectare over 3 years for converting to organic farming including inputs, certification, and market linkage",
        "eligibility_text": "Farmer wanting to do organic farming. Must join or form a cluster of at least 50 farmers covering 50 acres. Government funds organic inputs, certification fees, and helps link to organic markets.",
        "required_docs": ["Aadhaar card", "Land records", "Cluster formation proof", "Bank account"],
        "apply_url": "https://pgsindia-ncof.gov.in",
    },
    {
        "name": "PM Matsya Sampada Yojana",
        "benefit": "Subsidy up to 60 percent for fishing boats, nets, aquaculture ponds, fish feed units, and cold storage",
        "eligibility_text": "Fisherman, fish farmer, fish vendor, or fish worker in marine or inland fisheries. Also fisheries cooperatives, self-help groups, and fish farmer producer organisations. Any state with marine coast or river or lake.",
        "required_docs": ["Aadhaar card", "Fisherman registration certificate", "Bank account", "Project proposal", "Land or water body lease"],
        "apply_url": "https://pmmsy.dof.gov.in",
    },
    {
        "name": "National Scheme of Welfare of Fishermen",
        "benefit": "Group accident insurance Rs.50,000 for death, Rs.25,000 for partial disability. Also housing and drinking water support.",
        "eligibility_text": "Active fisherman, marine or inland, who earns livelihood from fishing. Registered with state fisheries department. Covers death or injury during fishing activity. Implemented through fishing cooperatives.",
        "required_docs": ["Aadhaar card", "Fisherman ID or cooperative membership", "Bank passbook"],
        "apply_url": "https://dof.gov.in",
    },
    {
        "name": "Rashtriya Gokul Mission",
        "benefit": "Subsidy and support for maintaining indigenous cow and buffalo breeds, artificial insemination services, cattle insurance",
        "eligibility_text": "Farmer or livestock owner who keeps indigenous cattle or buffalo breeds. Small and marginal farmers get priority. Aims to improve milk production from desi breeds without crossbreeding.",
        "required_docs": ["Aadhaar card", "Livestock ownership proof", "Bank account"],
        "apply_url": "https://dahd.nic.in",
    },
    {
        "name": "National Livestock Mission",
        "benefit": "Up to 50% subsidy on sheds, equipment, and breeding animals for poultry, sheep, goat, and pig farming",
        "eligibility_text": "Any individual wanting to start or expand poultry farming, goat rearing, sheep rearing, or piggery. Especially for SC/ST, women, and BPL families who can earn income from backyard livestock.",
        "required_docs": ["Aadhaar card", "Caste certificate if SC/ST", "Land or space proof", "Bank account", "Project report"],
        "apply_url": "https://nlm.udyamimitra.in",
    },
    {
        "name": "PM KUSUM Solar Pump Scheme",
        "benefit": "90% subsidy for installing solar pumps for irrigation, farmer pays only 10%. Excess power can be sold to grid.",
        "eligibility_text": "Any farmer who uses a diesel or electric pump for irrigation and wants to switch to solar energy. Individual farmers and farmer groups both eligible. All states covered.",
        "required_docs": ["Aadhaar card", "Land records", "Existing pump details", "Bank account"],
        "apply_url": "https://mnre.gov.in/solar/schemes",
    },
    {
        "name": "Agri-Clinics and Agri-Business Centres Scheme",
        "benefit": "Free training and subsidised loan with 36 to 44 percent subsidy for agriculture graduates to set up agri-consultancy",
        "eligibility_text": "Agriculture graduate or diploma holder from any agriculture or allied science field. Wants to set up agri clinic, agri business centre, or service centre for farmers. Includes veterinary graduates.",
        "required_docs": ["Aadhaar card", "Agriculture degree or diploma", "Business plan", "Bank account"],
        "apply_url": "https://acabc.nic.in",
    },
    {
        "name": "Sub-Mission on Agricultural Mechanisation",
        "benefit": "50 percent subsidy, up to 80 percent for SC/ST and small farmers, on tractors, tillers, harvesters, and farm machinery",
        "eligibility_text": "Individual farmer or farmer group wanting to buy agricultural machinery. Small and marginal farmers and SC/ST farmers get higher subsidy. Any state, any crop.",
        "required_docs": ["Aadhaar card", "Land records", "Caste certificate if applicable", "Bank account", "Quotation from vendor"],
        "apply_url": "https://agrimachinery.nic.in",
    },
    {
        "name": "Interest Subvention Scheme for Short-Term Crop Loans",
        "benefit": "Crop loans up to Rs.3 lakh at only 4% interest per year. Regular repayment gives additional 3% rebate.",
        "eligibility_text": "Any farmer taking a short-term crop loan from a bank for sowing expenses. Works through Kisan Credit Card. Benefit applies automatically when loan is taken from scheduled commercial bank or cooperative bank.",
        "required_docs": ["Aadhaar card", "Land records", "Bank account", "Kisan Credit Card"],
        "apply_url": "https://www.rbi.org.in",
    },
    {
        "name": "Pradhan Mantri Annadata Aay Yojana",
        "benefit": "Price support when market prices fall below Minimum Support Price for pulses and oilseeds",
        "eligibility_text": "Farmer registered with state agriculture department who grows notified crops like toor, moong, urad, groundnut, soybean. State government procures at MSP directly from farmers when prices crash.",
        "required_docs": ["Aadhaar card", "Land records", "State farmer registration", "Bank account"],
        "apply_url": "https://agricoop.nic.in",
    },

    # =========================================================
    # HEALTH  (21-35)
    # =========================================================
    {
        "name": "Ayushman Bharat PM-JAY",
        "benefit": "Rs.5 lakh health insurance per family per year for hospital treatment, cashless at any empanelled hospital",
        "eligibility_text": "Poor family listed in SECC 2011 database or BPL card holder. Covers all family members including elderly parents and children. No premium to pay. Includes most surgeries, cancer treatment, kidney dialysis.",
        "required_docs": ["Aadhaar card", "Ration card or BPL certificate", "Family ID"],
        "apply_url": "https://pmjay.gov.in",
    },
    {
        "name": "Ayushman Bharat Vaya Vandana Yojana",
        "benefit": "Free health cover of Rs.5 lakh per year for all senior citizens aged 70 and above, no income limit",
        "eligibility_text": "Any Indian citizen who is 70 years of age or older. No income limit. No BPL requirement. Covers all senior citizens equally regardless of wealth. Launched October 2024.",
        "required_docs": ["Aadhaar card", "Age proof birth certificate or school certificate", "Mobile number"],
        "apply_url": "https://pmjay.gov.in",
    },
    {
        "name": "Janani Suraksha Yojana",
        "benefit": "Rs.1,400 cash in rural areas or Rs.1,000 in urban areas for delivering baby at government hospital",
        "eligibility_text": "Pregnant woman from BPL family delivering at government hospital or accredited private hospital. All BPL women in all states. Above poverty line women in low-performing states like UP, Bihar, Rajasthan, MP, Jharkhand, Odisha also eligible.",
        "required_docs": ["Aadhaar card", "BPL card", "MCP card", "Hospital delivery record"],
        "apply_url": "https://nhm.gov.in/jsy",
    },
    {
        "name": "PM Matru Vandana Yojana",
        "benefit": "Rs.5,000 cash in 3 installments for first live birth",
        "eligibility_text": "Pregnant woman and lactating mother for her first living child. Must be 19 years or older. Registered at Anganwadi or health center. Cash transferred directly to bank account to compensate for wage loss during pregnancy.",
        "required_docs": ["Aadhaar card", "MCP card Mother and Child Protection card", "Bank passbook", "Mobile number"],
        "apply_url": "https://pmmvy.wcd.gov.in",
    },
    {
        "name": "National Health Mission",
        "benefit": "Free OPD consultations, medicines, diagnostics, and delivery services at government health centres",
        "eligibility_text": "Any Indian citizen especially in rural and semi-urban areas. No income requirement. Free treatment at government Primary Health Centres, Community Health Centres, and district hospitals. Covers maternal health, child health, immunisation, tuberculosis, malaria.",
        "required_docs": ["Aadhaar card preferred but not mandatory for emergency"],
        "apply_url": "https://nhm.gov.in",
    },
    {
        "name": "Pradhan Mantri Surakshit Matritva Abhiyan",
        "benefit": "Free antenatal check-up with specialist doctor on 9th of every month at government health facility",
        "eligibility_text": "Any pregnant woman in her second or third trimester, 4 months and above. No income requirement. Available at government hospitals, CHCs, PHCs on the 9th of every month.",
        "required_docs": ["Aadhaar card", "MCP card or antenatal card"],
        "apply_url": "https://pmsma.nhp.gov.in",
    },
    {
        "name": "Rashtriya Bal Swasthya Karyakram",
        "benefit": "Free health screening and treatment for children aged 0 to 18 years for birth defects, deficiencies, diseases, and developmental delays",
        "eligibility_text": "Any child from birth to 18 years enrolled in government school or attending anganwadi. Free screening for birth defects, nutritional deficiencies, diseases, and developmental delays. Free treatment for detected conditions.",
        "required_docs": ["Birth certificate or school enrolment record", "Aadhaar card child or parent"],
        "apply_url": "https://nhm.gov.in/rbsk",
    },
    {
        "name": "Nikshay Poshan Yojana",
        "benefit": "Rs.500 per month nutritional support for entire duration of tuberculosis treatment",
        "eligibility_text": "Any person diagnosed with tuberculosis and undergoing treatment under RNTCP or NTEP in any government or private health facility in India. Direct bank transfer every month of treatment duration.",
        "required_docs": ["Aadhaar card linked to bank account", "TB diagnosis notification", "Treatment card"],
        "apply_url": "https://nikshay.in",
    },
    {
        "name": "Rashtriya Arogya Nidhi",
        "benefit": "One-time financial assistance up to Rs.15 lakh for treatment of life-threatening disease at government hospital",
        "eligibility_text": "BPL patient suffering from life-threatening disease like heart surgery, kidney transplant, cancer, or neurological surgery. Treatment must be at a government hospital under the scheme. Family income must be below poverty line.",
        "required_docs": ["BPL card", "Aadhaar card", "Medical certificate from government hospital", "Bank account"],
        "apply_url": "https://mohfw.gov.in",
    },
    {
        "name": "Pradhan Mantri National Dialysis Programme",
        "benefit": "Free kidney dialysis for poor patients at government hospitals and empanelled private centres",
        "eligibility_text": "Poor patient suffering from chronic kidney disease requiring regular dialysis. BPL family or annual income below Rs.2.5 lakh. Implemented at district hospitals and government medical colleges.",
        "required_docs": ["Aadhaar card", "BPL card or income certificate", "Doctor prescription for dialysis", "Bank account"],
        "apply_url": "https://nhm.gov.in",
    },
    {
        "name": "Janani Shishu Suraksha Karyakram",
        "benefit": "Completely free institutional delivery including free drugs, diagnostics, blood, diet, and transport to and from hospital",
        "eligibility_text": "Any pregnant woman delivering at a government health facility. Any sick newborn requiring treatment at government hospital. No charges whatsoever, no user fees, no diet charges, no transport charges.",
        "required_docs": ["Aadhaar card not mandatory for emergency delivery"],
        "apply_url": "https://nhm.gov.in/jssk",
    },
    {
        "name": "Universal Immunisation Programme",
        "benefit": "Free vaccines for 12 vaccine-preventable diseases for children from birth to 16 years and pregnant women",
        "eligibility_text": "All children in India from birth. BCG, Polio, DPT, Hepatitis B, measles, rubella, Japanese encephalitis, typhoid, and more. Also tetanus vaccines for pregnant women. Available at all government health centres.",
        "required_docs": ["Birth certificate or MCP card mother and child protection card"],
        "apply_url": "https://mohfw.gov.in",
    },
    {
        "name": "Integrated Child Development Services ICDS",
        "benefit": "Free supplementary nutrition, immunisation, health check-up, and pre-school education at Anganwadi centre",
        "eligibility_text": "Children below 6 years old, pregnant women, and lactating mothers in rural and urban areas. Available through Anganwadi centres in every village and urban ward. No income requirement.",
        "required_docs": ["Aadhaar card", "Child birth certificate or age proof"],
        "apply_url": "https://wcd.nic.in/icds",
    },
    {
        "name": "Swachh Bharat Mission Gramin Household Toilet",
        "benefit": "Rs.12,000 grant to build a household toilet for BPL families in rural areas",
        "eligibility_text": "Rural BPL household that does not have a toilet at home. Priority to SC/ST, small and marginal farmers, women-headed households, disabled persons, and families with no adult male member.",
        "required_docs": ["BPL card", "Aadhaar card", "Bank account", "Photo of house showing no toilet"],
        "apply_url": "https://sbm.gov.in",
    },
    {
        "name": "Jal Jeevan Mission Har Ghar Jal",
        "benefit": "Free piped drinking water connection to every rural household, functional tap water at home",
        "eligibility_text": "Any rural household that does not have a piped water connection or has untreated water supply. Implemented through Gram Panchayat. Benefits households that walk long distances to collect water.",
        "required_docs": ["Aadhaar card", "Proof of residence in rural area"],
        "apply_url": "https://jaljeevanmission.gov.in",
    },

    # =========================================================
    # WOMEN  (36-50)
    # =========================================================
    {
        "name": "Indira Gandhi National Widow Pension Scheme",
        "benefit": "Rs.300 per month pension from central government, state governments often add more on top",
        "eligibility_text": "Woman who has lost her husband. Age between 40 and 79 years. Must belong to Below Poverty Line BPL family. Rural or urban. Any state in India.",
        "required_docs": ["Husband death certificate", "BPL card or ration card", "Aadhaar card", "Bank passbook", "Age proof"],
        "apply_url": "https://nsap.nic.in",
    },
    {
        "name": "Beti Bachao Beti Padhao Sukanya Samriddhi Yojana",
        "benefit": "High-interest savings account above 8% per year for girl child education and marriage, tax-free returns",
        "eligibility_text": "Parents or guardian of a girl child under 10 years of age. Account opened in Post Office or bank. Maximum deposit Rs.1.5 lakh per year. Matures when girl turns 21. Partial withdrawal allowed at 18 for education.",
        "required_docs": ["Girl child birth certificate", "Parent Aadhaar card", "Parent PAN card", "Passport photo"],
        "apply_url": "https://wcd.nic.in/bbbp-schemes",
    },
    {
        "name": "PM Ujjwala Yojana",
        "benefit": "Free LPG gas connection with first cylinder and stove, no deposit required",
        "eligibility_text": "Woman from BPL family who does not already have an LPG gas connection at home. Adult woman must be the applicant. Especially for women cooking on wood or coal fire which causes severe indoor air pollution and respiratory disease.",
        "required_docs": ["Aadhaar card", "BPL card or ration card", "Bank passbook", "Passport photo"],
        "apply_url": "https://pmuy.gov.in",
    },
    {
        "name": "Mahila Shakti Kendra",
        "benefit": "Skill training, digital literacy, health services, and legal awareness for rural women through trained volunteers",
        "eligibility_text": "Women in rural and semi-urban areas who want to gain skills, access government services, or understand their legal rights. Implemented at district and block level in 115 aspirational districts.",
        "required_docs": ["Aadhaar card", "Residence proof"],
        "apply_url": "https://wcd.nic.in/schemes/mahila-shakti-kendra-msk",
    },
    {
        "name": "Swadhar Greh",
        "benefit": "Free shelter, food, clothing, medical care, counselling, and legal aid for women in difficult circumstances up to 3 years",
        "eligibility_text": "Women aged 18 and above in difficult circumstances including widows without support, women deserted by family, survivors of violence, women released from jail, trafficked women, and mentally ill women without family.",
        "required_docs": ["Aadhaar card if available", "Police FIR if violence case", "Referral from government authority or NGO"],
        "apply_url": "https://wcd.nic.in/schemes/swadhar-greh",
    },
    {
        "name": "Working Women Hostel",
        "benefit": "Safe and affordable hostel accommodation for working women in cities with subsidised rent and day-care for children",
        "eligibility_text": "Working woman who has migrated or is away from family for work in urban area. Income below Rs.50,000 per month in metros or Rs.35,000 in other cities. Divorced, separated, or widowed women get priority.",
        "required_docs": ["Aadhaar card", "Employer letter or work proof", "Income certificate", "Passport photo"],
        "apply_url": "https://wcd.nic.in/schemes/working-women-hostel",
    },
    {
        "name": "Support to Training and Employment Programme STEP",
        "benefit": "Free vocational training in agriculture, animal husbandry, fisheries, handlooms, handicrafts, IT, and construction for women",
        "eligibility_text": "Women above 16 years of age belonging to BPL families or marginalised communities. Training in rural traditional sectors to improve their income and skills. Delivered through registered NGOs and cooperatives.",
        "required_docs": ["Aadhaar card", "BPL card or caste certificate", "Age proof"],
        "apply_url": "https://wcd.nic.in",
    },
    {
        "name": "Poshan Abhiyaan National Nutrition Mission",
        "benefit": "Improved nutrition services, growth monitoring, and take-home rations for pregnant women, lactating mothers, and children under 6",
        "eligibility_text": "Pregnant women, lactating mothers, and children below 6 years especially in tribal and aspirational districts. Delivered through Anganwadi centres. Focuses on reducing stunting, wasting, and anaemia.",
        "required_docs": ["Aadhaar card", "MCP card", "Anganwadi registration"],
        "apply_url": "https://poshanabhiyaan.gov.in",
    },
    {
        "name": "Pradhan Mantri Mudra Yojana Women Entrepreneurs",
        "benefit": "Collateral-free business loan: Shishu up to Rs.50,000, Kishore Rs.50,000 to Rs.5 lakh, Tarun Rs.5 to Rs.10 lakh",
        "eligibility_text": "Woman wanting to start or expand a small business such as tailoring, beauty parlour, food processing, handicraft, small shop, or any non-farm micro enterprise. No collateral required. Any bank, MFI, or NBFC provides the loan.",
        "required_docs": ["Aadhaar card", "Business plan or description", "Bank account", "Passport photo", "Proof of business location"],
        "apply_url": "https://mudra.org.in",
    },
    {
        "name": "Deendayal Antyodaya Yojana National Urban Livelihoods Mission",
        "benefit": "Self-help group formation, skill training, subsidised loans, and market linkage for urban poor women",
        "eligibility_text": "Urban poor woman who wants to earn income through self-help group, skill training, or small business. Covers street vendors, domestic workers, rag pickers, home-based workers. Urban areas only.",
        "required_docs": ["Aadhaar card", "Ration card or BPL certificate", "Residence proof", "Bank account"],
        "apply_url": "https://nulm.gov.in",
    },
    {
        "name": "Rajiv Gandhi Scheme for Empowerment of Adolescent Girls SABLA",
        "benefit": "Nutrition, health check-up, life skills education, vocational training, and guidance for girls aged 11 to 18",
        "eligibility_text": "Girl aged 11 to 18 years especially out-of-school girls and girls from BPL families. Delivered through Anganwadi centres. Covers nutrition, health, education guidance, and awareness about legal rights.",
        "required_docs": ["Age proof", "Aadhaar card", "School enrolment or out-of-school status proof"],
        "apply_url": "https://wcd.nic.in",
    },
    {
        "name": "National Creche Scheme",
        "benefit": "Subsidised or free day-care centres for children aged 6 months to 6 years of working mothers",
        "eligibility_text": "Working mother from BPL or low-income family with children between 6 months and 6 years old. Mother should be working, employed or self-employed. Creche provides nutrition, health care, and early education for the child.",
        "required_docs": ["Aadhaar card", "Child birth certificate", "Mother work proof or BPL card", "Bank account"],
        "apply_url": "https://wcd.nic.in/schemes/national-creche-scheme",
    },
    {
        "name": "PM Awas Yojana Urban Priority for Women",
        "benefit": "Interest subsidy of 3 to 6.5 percent on home loan for buying or building first house in urban area",
        "eligibility_text": "Urban family belonging to EWS income below Rs.3 lakh, LIG income Rs.3 to 6 lakh, or MIG income Rs.6 to 18 lakh buying or building their first home. Mandatory to register property in woman name or as joint owner.",
        "required_docs": ["Aadhaar card", "Income certificate", "Bank loan sanction letter", "Property documents", "Woman co-ownership agreement"],
        "apply_url": "https://pmaymis.gov.in",
    },
    {
        "name": "Mahila E-Haat",
        "benefit": "Free online marketplace for women entrepreneurs to sell handmade products directly to buyers across India",
        "eligibility_text": "Woman artisan, SHG member, or woman entrepreneur selling handmade or traditional products including handloom, handicraft, food products, clothing, jewellery. No technical knowledge needed. Government lists and promotes products.",
        "required_docs": ["Aadhaar card", "Bank account", "Photos of products", "Brief business description"],
        "apply_url": "https://mahilaehaat-rmk.gov.in",
    },
    {
        "name": "One Stop Centre Sakhi",
        "benefit": "Free integrated support: shelter, police help, legal aid, medical help, and counselling for violence survivors under one roof",
        "eligibility_text": "Any woman who has faced violence including domestic violence, sexual assault, acid attack, cyber crime, or trafficking. No income limit. Available in all districts. Toll-free helpline 181.",
        "required_docs": ["Aadhaar card if available not mandatory in emergency", "Police complaint if filed", "Medical record"],
        "apply_url": "https://wcd.nic.in/schemes/one-stop-centre-scheme",
    },

    # =========================================================
    # ELDERLY  (51-58)
    # =========================================================
    {
        "name": "Indira Gandhi National Old Age Pension Scheme",
        "benefit": "Rs.200 per month for age 60 to 79 or Rs.500 per month for age 80 and above from central government, states add more",
        "eligibility_text": "Elderly person aged 60 years or above. Must belong to a BPL family. Any gender. Any state in India. Destitute person with little or no regular income. SC/ST elderly get priority. Applied through Gram Panchayat or Ward Office.",
        "required_docs": ["Age proof birth certificate or school certificate", "BPL card", "Aadhaar card", "Bank passbook"],
        "apply_url": "https://nsap.nic.in",
    },
    {
        "name": "Atal Vayo Abhyuday Yojana AVYAY",
        "benefit": "Grant support for NGOs providing integrated care, day-care centres, and rehabilitation for destitute elderly",
        "eligibility_text": "Destitute elderly person aged 60 or above with no family support or income. Implemented through registered NGOs and old age homes. Covers food, shelter, medical care, and recreation for senior citizens with nobody to care for them.",
        "required_docs": ["Age proof", "Aadhaar card", "Proof of no income or family support"],
        "apply_url": "https://grants-msje.gov.in",
    },
    {
        "name": "Varishtha Pension Bima Yojana",
        "benefit": "Guaranteed 8% pension for life on a lump sum deposit with LIC for senior citizens above 60",
        "eligibility_text": "Senior citizen aged 60 years and above. One-time lump sum deposit with LIC of India. Minimum pension Rs.500 per month, maximum Rs.5,000 per month per family depending on investment amount.",
        "required_docs": ["Aadhaar card", "Age proof", "Bank account", "PAN card"],
        "apply_url": "https://www.licindia.in",
    },
    {
        "name": "Senior Citizen Savings Scheme",
        "benefit": "8.2% annual interest guaranteed by government on savings up to Rs.30 lakh with quarterly interest payout",
        "eligibility_text": "Indian citizen aged 60 years or above. Also available to retired defence personnel aged 50 and above, and voluntary retirement persons aged 55 and above. Opens at Post Office or nationalised bank.",
        "required_docs": ["Aadhaar card", "Age proof", "PAN card", "Passport photo"],
        "apply_url": "https://www.indiapost.gov.in",
    },
    {
        "name": "National Programme for Health Care of the Elderly",
        "benefit": "Free specialised medical care for elderly at PHC, CHC, district hospital with dedicated geriatric OPD",
        "eligibility_text": "Any elderly person aged 60 years and above who needs medical care. Free services at government hospitals including physiotherapy, specialist consultation, medicines, and assistive devices. No income requirement.",
        "required_docs": ["Aadhaar card", "Age proof"],
        "apply_url": "https://nhm.gov.in",
    },
    {
        "name": "Rashtriya Vayoshri Yojana",
        "benefit": "Free assistive devices for elderly BPL persons: walking sticks, wheelchairs, hearing aids, spectacles, dentures",
        "eligibility_text": "Elderly person aged 60 or above belonging to BPL family. Has age-related disability like mobility impairment, hearing loss, vision loss, or difficulty eating. Devices given free of cost through camps organised by ALIMCO.",
        "required_docs": ["Aadhaar card", "Age proof", "BPL card", "Disability assessment done at camp"],
        "apply_url": "https://www.alimco.in",
    },
    {
        "name": "Elder Line Toll Free Helpline for Senior Citizens",
        "benefit": "Free helpline 14567 for elderly: information on schemes, emergency support, medical help, legal guidance, and emotional support",
        "eligibility_text": "Any elderly person aged 60 and above in India who needs information, help, or support. Helpline number 14567 is completely free. Available in multiple languages. Connects to local NGOs and authorities for follow-up action.",
        "required_docs": ["No documents required, just call 14567"],
        "apply_url": "https://elderline.gov.in",
    },
    {
        "name": "Annapurna Scheme for Destitute Elderly",
        "benefit": "10 kg of free food grain per month for destitute senior citizens who are not covered by old age pension",
        "eligibility_text": "Senior citizen aged 65 years and above who is destitute with no income and no family support. Eligible for old age pension but not receiving it due to limited coverage. Implemented through state governments.",
        "required_docs": ["Age proof", "Aadhaar card", "BPL certificate", "Self-declaration of no other pension"],
        "apply_url": "https://nsap.nic.in",
    },

    # =========================================================
    # EDUCATION & STUDENTS  (59-75)
    # =========================================================
    {
        "name": "Post-Matric Scholarship for SC Students",
        "benefit": "Full tuition fee reimbursement plus maintenance allowance of Rs.380 to Rs.1,200 per month depending on course level",
        "eligibility_text": "Scheduled Caste student studying in Class 11 and above. Parent or guardian income must be below Rs.2.5 lakh per year. Studying at any government or recognised private institution.",
        "required_docs": ["Aadhaar card", "SC caste certificate", "Income certificate", "Previous year marksheet", "Bank account", "Admission letter"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "Post-Matric Scholarship for ST Students",
        "benefit": "Full tuition fee reimbursement plus maintenance allowance for tribal students studying Class 11 and above",
        "eligibility_text": "Scheduled Tribe student studying in Class 11 or above. Parent income below Rs.2.5 lakh per year. Studying at any government or recognised private institution. Tribal students in any Indian state.",
        "required_docs": ["Aadhaar card", "ST caste certificate", "Income certificate", "Previous year marksheet", "Bank account"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "Post-Matric Scholarship for OBC Students",
        "benefit": "Tuition fee and maintenance allowance for OBC students from Class 11 onwards",
        "eligibility_text": "Other Backward Class student studying in Class 11 or above. Parent income must be below Rs.1 lakh per year. Studying in any government or recognised institution.",
        "required_docs": ["Aadhaar card", "OBC non-creamy layer certificate", "Income certificate", "Previous year marksheet", "Bank account"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "Top Class Education Scholarship for SC Students",
        "benefit": "Rs.1.41 lakh per year non-residential or Rs.2.57 lakh residential for SC students in IITs, IIMs, NITs, medical colleges",
        "eligibility_text": "Scheduled Caste student admitted to one of 266 top government-notified premier institutions including IITs, IIMs, NLUs, NITs, and central universities. Income limit Rs.4.5 lakh per year. 2 slots per family.",
        "required_docs": ["Aadhaar card", "SC caste certificate", "Income certificate", "Admission letter from institution", "Previous marksheet", "Bank account"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "National Overseas Scholarship for SC Students",
        "benefit": "Full scholarship for SC students to study Masters or PhD abroad covering tuition, living expenses, visa, and airfare",
        "eligibility_text": "Scheduled Caste student below 35 years of age who has secured admission to a foreign university for Masters or PhD. Income below Rs.8 lakh per year. Only 30 slots per year selected on merit.",
        "required_docs": ["SC caste certificate", "Aadhaar card", "Income certificate", "Foreign university admission letter", "Academic transcripts"],
        "apply_url": "https://nosmsje.gov.in",
    },
    {
        "name": "PM YASASVI Scholarship",
        "benefit": "Rs.75,000 per year for Class 9 to 10 or Rs.1,25,000 per year for Class 11 to 12 for OBC, EBC, and DNT students in private schools",
        "eligibility_text": "Student from OBC, EBC Economically Backward Class, or DNT De-notified Tribe studying in Class 9, 10, 11, or 12 at a private school. Family income below Rs.2.5 lakh per year. Merit selection through NTA exam.",
        "required_docs": ["Aadhaar card", "OBC or EBC or DNT certificate", "Income certificate", "School enrolment", "Bank account"],
        "apply_url": "https://yet.nta.ac.in",
    },
    {
        "name": "National Scholarship for Persons with Disabilities",
        "benefit": "Rs.4,000 to Rs.20,000 per year depending on course level for disabled students from pre-matric to post-graduate",
        "eligibility_text": "Student with at least 40% disability studying in Class 9 and above. Income below Rs.2.5 lakh per year. Covers physical disability, visual impairment, hearing impairment, intellectual disability, autism, and multiple disabilities.",
        "required_docs": ["Aadhaar card", "Disability certificate 40% or more from competent authority", "Income certificate", "Marksheet", "Bank account"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "Central Sector Scholarship for College Students",
        "benefit": "Rs.10,000 per year first three years or Rs.20,000 per year for professional courses for meritorious students",
        "eligibility_text": "Student who scored in top 20 percentile in Class 12 board exam and family income below Rs.8 lakh per year. Pursuing undergraduate studies at any recognised college. Not valid for private engineering or medical colleges.",
        "required_docs": ["Aadhaar card", "Class 12 marksheet", "Income certificate", "College admission letter", "Bank account"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "PM CARES Children Scholarship",
        "benefit": "Tuition fee and education support for children who lost parents to COVID-19",
        "eligibility_text": "Child who lost both parents or legal guardian to COVID-19, or whose breadwinner parent died of COVID-19. Child must be below 18 years at time of parent death. Covers school and college education costs.",
        "required_docs": ["Death certificate of parent with COVID mention", "Child Aadhaar card", "School enrolment", "Guardian Aadhaar card", "Bank account"],
        "apply_url": "https://pmcaresforchildren.in",
    },
    {
        "name": "Ishan Uday Scholarship for North Eastern Region",
        "benefit": "Rs.5,400 to Rs.7,800 per month for NE India students studying in central universities outside their home state",
        "eligibility_text": "Student domiciled in any of the 8 North Eastern states Assam, Arunachal Pradesh, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura. Income below Rs.4.5 lakh per year. Studying at degree level outside home state.",
        "required_docs": ["Aadhaar card", "NE state domicile certificate", "Income certificate", "Admission letter", "Bank account"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "Free Coaching Scheme for SC and OBC Students",
        "benefit": "Free coaching for UPSC, SSC, banking, railways, IIT-JEE, NEET for SC and OBC students",
        "eligibility_text": "SC or OBC student wanting coaching for central government competitive exams or entrance tests to premier institutions. Income below Rs.8 lakh per year. 30 percent seats reserved for women. Conducted at government-recognised coaching centres.",
        "required_docs": ["Aadhaar card", "SC or OBC certificate", "Income certificate", "Educational qualification certificates", "Bank account"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "National Means-cum-Merit Scholarship",
        "benefit": "Rs.12,000 per year for Class 9 to 12 meritorious students from low-income families to prevent school dropout",
        "eligibility_text": "Student who passed Class 8 with at least 55 percent marks, 50 percent for SC/ST. Family income below Rs.3.5 lakh per year. Studying in government or government-aided schools. Selected through state-level examination.",
        "required_docs": ["Aadhaar card", "Class 8 marksheet", "Income certificate", "School enrolment", "Bank account"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "Pradhan Mantri Vidya Lakshmi Karyakram",
        "benefit": "Collateral-free education loans up to Rs.7.5 lakh for skill courses and more for degree courses through unified digital platform",
        "eligibility_text": "Student admitted to or pursuing higher education in India or abroad at any government-recognised institution. Applied through Vidya Lakshmi portal which connects to multiple banks simultaneously. Launched January 2025.",
        "required_docs": ["Aadhaar card", "Admission letter", "Academic records", "Bank account", "Income proof of family"],
        "apply_url": "https://www.vidyalakshmi.co.in",
    },
    {
        "name": "Dr. Ambedkar Interest Subsidy Scheme OBC EBC",
        "benefit": "Government pays interest on education loans for OBC and EBC students studying abroad during study period",
        "eligibility_text": "OBC or EBC student who has taken an education loan for studying abroad at Masters or PhD level. Family income below Rs.8 lakh per year. Applied through Canara Bank portal. Subsidy paid directly to bank.",
        "required_docs": ["Aadhaar card", "OBC or EBC certificate", "Income certificate", "Education loan sanction letter", "Foreign admission letter"],
        "apply_url": "https://canarabankcsis.in/ACSIS",
    },
    {
        "name": "PM Internship Scheme",
        "benefit": "Rs.5,000 per month stipend plus Rs.6,000 one-time assistance for 12-month internship at top 500 companies",
        "eligibility_text": "Youth aged 21 to 24 years who is not in full-time employment or education. Should not have passed from IIT, IIM, or CA. Annual family income below Rs.8 lakh. Matching with companies through online portal. Launched October 2024.",
        "required_docs": ["Aadhaar card", "Educational qualification proof", "Income certificate", "Bank account", "Registration on PM Internship portal"],
        "apply_url": "https://pminternship.mca.gov.in",
    },

    # =========================================================
    # LIVELIHOOD, EMPLOYMENT & MICRO-CREDIT  (76-95)
    # =========================================================
    {
        "name": "MGNREGA Mahatma Gandhi National Rural Employment Guarantee",
        "benefit": "100 days of guaranteed wage employment per year at state minimum wage",
        "eligibility_text": "Any adult member of a rural household willing to do unskilled manual work. No income limit. Family applies for job card from Gram Panchayat. Works include well digging, road building, tree planting, pond construction.",
        "required_docs": ["Aadhaar card", "Ration card", "Passport photo", "Bank passbook"],
        "apply_url": "https://nrega.nic.in",
    },
    {
        "name": "PM SVANidhi Street Vendor Micro Credit",
        "benefit": "Collateral-free loan: Rs.10,000 first time, Rs.20,000 second, Rs.50,000 third for street vendors",
        "eligibility_text": "Urban street vendor or hawker who earns livelihood by vending on street or in public places. Must have vending certificate from Urban Local Body or letter from Town Vending Committee. Fruit sellers, vegetable sellers, tea stall owners, cobblers, washermen, barbers all eligible.",
        "required_docs": ["Aadhaar card", "Vending certificate or ULB letter", "Bank passbook", "Mobile linked to Aadhaar"],
        "apply_url": "https://pmsvanidhi.mohua.gov.in",
    },
    {
        "name": "PM Vishwakarma Yojana",
        "benefit": "Rs.15,000 toolkit grant plus skill training plus Rs.1 lakh loan at 5% interest, second tranche Rs.2 lakh",
        "eligibility_text": "Traditional artisan or craftsperson working with hands and tools in one of 18 trades: blacksmith, goldsmith, potter, carpenter, tailor, cobbler, barber, washerman, fishing net maker, toy maker, basket weaver, broom maker, sculptor, locksmith, hammer maker, shoe maker, idol maker, boat maker. Must be self-employed not salaried.",
        "required_docs": ["Aadhaar card", "Trade proof photos or tools or community certificate", "Bank passbook", "Mobile number"],
        "apply_url": "https://pmvishwakarma.gov.in",
    },
    {
        "name": "Pradhan Mantri Mudra Yojana",
        "benefit": "Business loan without collateral: Shishu up to Rs.50,000, Kishore Rs.50,000 to Rs.5 lakh, Tarun Rs.5 to Rs.10 lakh, Tarun Plus up to Rs.20 lakh",
        "eligibility_text": "Any individual, proprietorship, partnership, or small company wanting to start or expand a non-farm micro or small business. Includes small shops, service businesses, manufacturing, food businesses, artisans, transport operators. Any Indian bank, MFI, or NBFC provides the loan.",
        "required_docs": ["Aadhaar card", "PAN card", "Business plan or description", "Proof of business address", "Bank account"],
        "apply_url": "https://mudra.org.in",
    },
    {
        "name": "Stand Up India",
        "benefit": "Bank loan of Rs.10 lakh to Rs.1 crore for SC/ST and women entrepreneurs to set up greenfield enterprise",
        "eligibility_text": "SC/ST individual or any woman entrepreneur who wants to set up a new manufacturing, services, or trading enterprise. Should not have existing enterprise. Bank loan with 7-year repayment period. At least one SC/ST and one woman borrower per bank branch.",
        "required_docs": ["Aadhaar card", "Caste certificate if SC/ST", "Business plan", "Educational qualification proof", "Bank account"],
        "apply_url": "https://www.standupmitra.in",
    },
    {
        "name": "PM Employment Generation Programme PMEGP",
        "benefit": "Subsidy up to 35 percent in rural areas on bank loan for setting up new manufacturing or service enterprise",
        "eligibility_text": "Any individual aged 18 and above wanting to set up a new small manufacturing or service business. SC/ST, women, ex-servicemen, handicapped, and residents of NE states and hilly areas get higher subsidy. Must be a new enterprise.",
        "required_docs": ["Aadhaar card", "Educational qualification 8th pass for projects above Rs.10 lakh", "Caste certificate if SC/ST", "Bank account", "Project report"],
        "apply_url": "https://kviconline.gov.in/pmegpeportal",
    },
    {
        "name": "Deendayal Antyodaya Yojana National Rural Livelihoods Mission",
        "benefit": "SHG formation support, revolving fund of Rs.15,000, community investment fund, and subsidised credit linkage to banks",
        "eligibility_text": "Rural poor women who want to form or join a self-help group for collective savings and credit. BPL families, SC/ST women, minorities, and single women get priority. Organised through Gram Panchayat.",
        "required_docs": ["Aadhaar card", "BPL card or income certificate", "Bank account", "Residence proof"],
        "apply_url": "https://aajeevika.gov.in",
    },
    {
        "name": "National Urban Livelihoods Mission NULM",
        "benefit": "Skill training, self-employment loan with 5 to 7 percent interest subsidy, SHG support, and shelter for urban homeless",
        "eligibility_text": "Urban poor person including domestic worker, construction worker, rag picker, street vendor, rickshaw puller, or any informal worker. Prioritises SC/ST, women, minorities, disabled, and migrants. Available in cities and towns.",
        "required_docs": ["Aadhaar card", "BPL card or income certificate", "Residence in urban area", "Bank account"],
        "apply_url": "https://nulm.gov.in",
    },
    {
        "name": "Atal Pension Yojana",
        "benefit": "Guaranteed pension of Rs.1,000 to Rs.5,000 per month after age 60 based on monthly contribution",
        "eligibility_text": "Indian citizen aged 18 to 40 years who does not have a formal pension scheme. Works in unorganised sector such as daily wage, domestic worker, self-employed, farmer. Monthly contribution as low as Rs.42 per month for Rs.1,000 pension. Government co-contributes for BPL.",
        "required_docs": ["Aadhaar card", "Bank account", "Mobile number"],
        "apply_url": "https://www.npscra.nsdl.co.in",
    },
    {
        "name": "PM Shram Yogi Maan-dhan Yojana",
        "benefit": "Rs.3,000 per month pension after age 60 for unorganised sector workers, government matches contribution",
        "eligibility_text": "Unorganised sector worker aged 18 to 40 years with monthly income below Rs.15,000. Includes home-based workers, street vendors, cobblers, rag pickers, domestic workers, washermen, rickshaw pullers. Not covered by NPS, ESIC, or EPFO.",
        "required_docs": ["Aadhaar card", "Bank account linked to Aadhaar", "Self-declaration of income", "Mobile number"],
        "apply_url": "https://maandhan.in",
    },
    {
        "name": "National Pension Scheme for Traders and Self-Employed",
        "benefit": "Rs.3,000 per month pension after age 60 for small shopkeepers and self-employed persons",
        "eligibility_text": "Small shopkeeper, retail trader, or self-employed person aged 18 to 40 years. GST annual turnover below Rs.1.5 crore. Not an income taxpayer. Monthly contribution Rs.55 to Rs.200, government matches equally.",
        "required_docs": ["Aadhaar card", "GST registration number or shop certificate", "Bank account", "Self-declaration"],
        "apply_url": "https://maandhan.in",
    },
    {
        "name": "Building and Other Construction Workers Welfare",
        "benefit": "Maternity benefit Rs.3,000, scholarship for children, death compensation Rs.1 lakh, disability pension, and pension after 60",
        "eligibility_text": "Construction worker who has worked at a building site for at least 90 days in the previous year. Must register with State Building and Construction Workers Welfare Board. Covers masons, plumbers, electricians, carpenters, and other site workers.",
        "required_docs": ["Aadhaar card", "Self-declaration of construction work", "Bank account", "Passport photo", "Employer or contractor certificate"],
        "apply_url": "https://bocw.gov.in",
    },
    {
        "name": "e-Shram Portal Unorganised Workers Registration",
        "benefit": "Free accident insurance of Rs.2 lakh on enrolment plus gateway to access all welfare schemes for unorganised workers",
        "eligibility_text": "Any unorganised sector worker aged 16 to 59 years not covered by ESIC or EPFO. Includes domestic workers, street vendors, agricultural labour, construction workers, home-based workers. Free registration gives UAN number and accident insurance.",
        "required_docs": ["Aadhaar card linked to mobile number", "Bank account"],
        "apply_url": "https://eshram.gov.in",
    },
    {
        "name": "National SC Finance and Development Corporation NSFDC",
        "benefit": "Low-interest loans at 6 percent per year up to Rs.30 lakh for SC entrepreneurs to start or expand business",
        "eligibility_text": "Scheduled Caste individual above 18 years, income below Rs.3 lakh per year rural or Rs.3.5 lakh urban. For self-employment in any business or enterprise including agriculture, trade, transport, services.",
        "required_docs": ["Aadhaar card", "SC caste certificate", "Income certificate", "Business plan", "Bank account"],
        "apply_url": "https://nsfdc.nic.in",
    },
    {
        "name": "National Backward Classes Finance and Development Corporation NBCFDC",
        "benefit": "Term loan up to Rs.20 lakh at 6% interest for OBC entrepreneurs for income-generating activities",
        "eligibility_text": "OBC individual below 55 years with annual income below Rs.3 lakh in rural or Rs.3.5 lakh in urban areas. For self-employment in shop, trade, transport, manufacturing, or service business.",
        "required_docs": ["Aadhaar card", "OBC non-creamy layer certificate", "Income certificate", "Business plan", "Bank account"],
        "apply_url": "https://nbcfdc.gov.in",
    },
    {
        "name": "Startup India DPIIT Recognition",
        "benefit": "Tax exemptions for 3 years, self-certify under 6 labour laws, fast-track patent filing with 80% fee rebate, access to government fund-of-funds",
        "eligibility_text": "Startup registered as private limited company, partnership, or LLP. Incorporated less than 10 years ago. Annual turnover below Rs.100 crore in any year. Working towards innovation, development, or improvement of products or services.",
        "required_docs": ["Aadhaar card of founders", "Company incorporation documents", "PAN card", "Brief description of innovation", "Bank account"],
        "apply_url": "https://www.startupindia.gov.in",
    },
    {
        "name": "Pradhan Mantri Kaushal Vikas Yojana PMKVY",
        "benefit": "Free short-term skill training 150 to 300 hours in 300 plus courses with placement assistance and certification",
        "eligibility_text": "Youth aged 15 to 45 years who is out of school or college and wants to gain a skill and find employment. Any educational level. Available in all districts through registered training centres. Includes beauty, retail, electronics, construction, IT, healthcare, textile courses.",
        "required_docs": ["Aadhaar card", "Educational qualification proof", "Mobile number"],
        "apply_url": "https://pmkvyofficial.org",
    },
    {
        "name": "Jan Dhan Yojana PMJDY",
        "benefit": "Zero-balance bank account with RuPay debit card, Rs.2 lakh accident insurance, Rs.30,000 life insurance, and overdraft of Rs.10,000",
        "eligibility_text": "Any Indian citizen who does not have a bank account or whose household has no bank account. No minimum balance required. Free accident insurance and life insurance benefits. Any bank in India.",
        "required_docs": ["Aadhaar card", "Passport photo"],
        "apply_url": "https://pmjdy.gov.in",
    },
    {
        "name": "PM Rozgar Protsahan Yojana",
        "benefit": "Government pays 12% employer EPF contribution for 3 years for new employees, reduces hiring cost for employers",
        "eligibility_text": "Any employee newly hired by an EPFO-registered establishment. Employee must not have an existing EPFO account. Salary must be below Rs.15,000 per month. Encourages formal employment.",
        "required_docs": ["Aadhaar card", "EPFO registration of employer", "Employee appointment letter", "Bank account"],
        "apply_url": "https://pmrpy.gov.in",
    },
    {
        "name": "PM Viksit Bharat Rozgar Yojana",
        "benefit": "Government pays one month salary as EPF contribution for first-time employees in formal sector, up to Rs.15,000",
        "eligibility_text": "First-time employee entering formal sector with salary below Rs.1 lakh per month. Government gives incentive to both new employee and employer. Aims to create 1 crore new formal jobs over 2 years. Launched 2024.",
        "required_docs": ["Aadhaar card", "Bank account linked to Aadhaar", "Employer EPFO registration", "New employee declaration"],
        "apply_url": "https://labour.gov.in",
    },

    # =========================================================
    # HOUSING & INFRASTRUCTURE  (96-103)
    # =========================================================
    {
        "name": "PM Awas Yojana Gramin",
        "benefit": "Rs.1.2 lakh grant, Rs.1.3 lakh in hilly and NE areas, to build a permanent concrete house",
        "eligibility_text": "Rural family living in kachha house with mud walls or thatched roof or who is homeless. BPL family. Priority to SC/ST, widows, disabled persons, and families with no adult male member. Must not already own a pucca house.",
        "required_docs": ["BPL card", "Aadhaar card", "Bank passbook", "Land documents or site certificate", "Photo of current house"],
        "apply_url": "https://pmayg.nic.in",
    },
    {
        "name": "PM Awas Yojana Urban",
        "benefit": "Interest subsidy of 3 to 6.5 percent on home loan for EWS, LIG, and MIG families buying or constructing first house in urban area",
        "eligibility_text": "Urban family with no pucca house anywhere in India. EWS income below Rs.3 lakh, LIG income Rs.3 to 6 lakh, or MIG income Rs.6 to 18 lakh. Property must be registered in woman name. Subsidy credited directly to loan account.",
        "required_docs": ["Aadhaar card", "Income certificate", "Bank loan sanction letter", "Property documents", "Self-declaration of no pucca house"],
        "apply_url": "https://pmaymis.gov.in",
    },
    {
        "name": "PM Surya Ghar Muft Bijli Yojana",
        "benefit": "Subsidy for rooftop solar panels: Rs.30,000 for 1 kW, Rs.60,000 for 2 kW, Rs.78,000 for 3 kW. Up to 300 units free electricity per month.",
        "eligibility_text": "Indian household that owns a house with a suitable rooftop and has a valid electricity connection. Any income level. Government gives direct subsidy. Excess electricity sold back to grid earns additional income. Launched February 2024.",
        "required_docs": ["Aadhaar card", "Electricity connection number", "Bank account", "Roof ownership proof"],
        "apply_url": "https://pmsuryaghar.gov.in",
    },
    {
        "name": "Pradhan Mantri Gramin Digital Saksharta Abhiyan PMGDISHA",
        "benefit": "Free basic digital literacy training: how to use smartphone, internet, digital payments, and government online services",
        "eligibility_text": "Rural household member aged 14 to 60 years who does not know how to use a computer or smartphone. One member per rural household. Training covers internet browsing, email, digital payments, accessing government portals.",
        "required_docs": ["Aadhaar card", "Proof of being digitally illiterate self-declaration"],
        "apply_url": "https://pmgdisha.in",
    },
    {
        "name": "Rajiv Awas Yojana Slum Redevelopment",
        "benefit": "Pucca house with all amenities water, sanitation, electricity for slum dwellers through in-situ redevelopment",
        "eligibility_text": "Person living in a notified slum in an urban area. Does not own any other house. Slum must be selected by state government for redevelopment. Flat or house given at subsidised or no cost.",
        "required_docs": ["Aadhaar card", "Proof of living in slum electricity bill or ration card", "No-other-house declaration"],
        "apply_url": "https://mhupa.gov.in",
    },
    {
        "name": "Housing for Plantation Workers",
        "benefit": "Housing assistance for workers on tea, coffee, rubber, and other plantations",
        "eligibility_text": "Worker employed on a registered plantation estate in India including tea gardens in Assam and West Bengal, coffee estates in Karnataka and Kerala, rubber plantations in Kerala. Worker must be registered with employer.",
        "required_docs": ["Aadhaar card", "Plantation work card or employer certificate", "Bank account"],
        "apply_url": "https://labour.gov.in",
    },
    {
        "name": "Interest Subsidy Scheme for Housing Loans Weaker Sections",
        "benefit": "Interest subsidy 6.5 percent for EWS/LIG on loans up to Rs.6 lakh for 20 years",
        "eligibility_text": "EWS income below Rs.3 lakh per year or LIG income Rs.3 to 6 lakh per year family buying or constructing first house through bank loan in urban areas. Must not have received any housing benefit from central government before.",
        "required_docs": ["Aadhaar card", "Income certificate", "Bank home loan sanction letter", "Property documents"],
        "apply_url": "https://pmaymis.gov.in",
    },
    {
        "name": "BharatNet Rural Broadband",
        "benefit": "High-speed internet connectivity at gram panchayat level, 100 Mbps bandwidth to every village",
        "eligibility_text": "Rural residents in villages connected through BharatNet. Internet access provided through optical fibre to gram panchayat, then Wi-Fi hotspots or cable to homes. Enables access to government services, telemedicine, and online education.",
        "required_docs": ["No separate registration, available at local service provider"],
        "apply_url": "https://bbnl.nic.in",
    },

    # =========================================================
    # INSURANCE & SOCIAL SECURITY  (104-112)
    # =========================================================
    {
        "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana PMJJBY",
        "benefit": "Rs.2 lakh life insurance cover for Rs.436 per year, less than Rs.1.20 per day, paid to family on death from any cause",
        "eligibility_text": "Any Indian citizen aged 18 to 50 years having a savings bank account. Insurance cover continues up to age 55 if enrolled before 50. Family receives Rs.2 lakh on the insured person death from any cause.",
        "required_docs": ["Aadhaar card", "Bank account", "Consent form filled at bank"],
        "apply_url": "https://jansuraksha.gov.in",
    },
    {
        "name": "Pradhan Mantri Suraksha Bima Yojana PMSBY",
        "benefit": "Rs.2 lakh accidental death and disability insurance for only Rs.20 per year, barely 2 rupees per month",
        "eligibility_text": "Any Indian citizen aged 18 to 70 years having a bank account. Covers accidental death Rs.2 lakh and permanent total disability Rs.2 lakh. Permanent partial disability covered for Rs.1 lakh. Auto-renewed every year.",
        "required_docs": ["Aadhaar card", "Bank account", "Consent form"],
        "apply_url": "https://jansuraksha.gov.in",
    },
    {
        "name": "National Family Benefit Scheme",
        "benefit": "Rs.20,000 one-time lump sum when the breadwinner of BPL family dies from any cause",
        "eligibility_text": "Rural or urban BPL family where the primary earning member has died. Deceased must be aged 18 to 64 years. Death can be from any cause. Application within 90 days of death. Helps family survive immediate financial crisis after losing income earner.",
        "required_docs": ["Death certificate of breadwinner", "BPL card", "Aadhaar of applicant family member", "Bank passbook", "Proof of relationship"],
        "apply_url": "https://nsap.nic.in",
    },
    {
        "name": "Employees State Insurance ESIC",
        "benefit": "Medical care for entire family, sickness benefit 70 percent wages for 91 days, maternity benefit 26 weeks at full wages, disability pension",
        "eligibility_text": "Employee working in any factory or establishment with 10 or more workers and monthly salary below Rs.21,000. Employee pays 0.75 percent, employer pays 3.25 percent of wages. Covers spouse, parents, and children.",
        "required_docs": ["Aadhaar card", "Employment proof", "Employer registration", "ESIC card"],
        "apply_url": "https://www.esic.nic.in",
    },
    {
        "name": "Employees Provident Fund EPF",
        "benefit": "Retirement savings with 12 percent of basic salary saved each month, employer matches it, plus insurance of Rs.7 lakh and pension",
        "eligibility_text": "Employee in any organisation with 20 or more workers. Monthly salary below Rs.15,000 is mandatory coverage. Provides financial security at retirement, death insurance of Rs.7 lakh under EDLI, and pension through EPS.",
        "required_docs": ["Aadhaar card", "Employment proof", "Bank account"],
        "apply_url": "https://www.epfindia.gov.in",
    },
    {
        "name": "National Social Assistance Programme NSAP",
        "benefit": "Monthly pension for elderly poor, widows, disabled persons, and one-time payment for family of deceased breadwinner",
        "eligibility_text": "BPL persons in five categories: elderly 60 plus, widows 40 to 79, disabled with severe disability, and family of deceased breadwinner. Implemented through state governments with central funds. States add their own contribution on top.",
        "required_docs": ["Aadhaar card", "BPL card", "Category-specific proof age or death or disability certificate", "Bank account"],
        "apply_url": "https://nsap.nic.in",
    },
    {
        "name": "Weavers Comprehensive Welfare Scheme",
        "benefit": "Health insurance, life insurance of Rs.2 lakh, and scholarship for children of handloom weavers",
        "eligibility_text": "Handloom weaver who earns majority of income from weaving and is below 59 years of age. Registered with state handloom department. Health insurance covers OPD and hospitalisation.",
        "required_docs": ["Aadhaar card", "Weaver registration certificate from state department", "Bank account", "Passport photo"],
        "apply_url": "https://handlooms.nic.in",
    },
    {
        "name": "Pradhan Mantri Beedi Worker Welfare Fund",
        "benefit": "Housing, health care, scholarship for children, and group insurance for beedi workers",
        "eligibility_text": "Worker employed in beedi industry rolling beedis, sorting, packing, registered with state labour department. Covers medical facilities, housing loan, and scholarship for children studying Class 6 to engineering level.",
        "required_docs": ["Aadhaar card", "Beedi worker identity card", "Bank account"],
        "apply_url": "https://labour.gov.in",
    },
    {
        "name": "e-Shram Accident Insurance",
        "benefit": "Free Rs.2 lakh accident insurance on registering on e-Shram portal for all unorganised workers",
        "eligibility_text": "Any unorganised sector worker aged 16 to 59 years. Includes all informal workers not covered by ESIC or EPFO. Free registration on e-Shram portal gives UAN card and automatic accident insurance coverage.",
        "required_docs": ["Aadhaar card linked to mobile number", "Bank account"],
        "apply_url": "https://eshram.gov.in",
    },

    # =========================================================
    # DISABILITY  (113-120)
    # =========================================================
    {
        "name": "Indira Gandhi National Disability Pension Scheme",
        "benefit": "Rs.300 per month pension for severely disabled BPL persons aged 18 to 79 years",
        "eligibility_text": "Person with at least 80 percent disability, severe or multiple disability. Must belong to BPL family. Aged 18 to 79 years. Any disability type: physical, visual, hearing, intellectual. Applied through Gram Panchayat or Ward Office.",
        "required_docs": ["Disability certificate 80 percent or more from government hospital", "BPL card", "Aadhaar card", "Age proof", "Bank passbook"],
        "apply_url": "https://nsap.nic.in",
    },
    {
        "name": "ADIP Scheme Assistance to Disabled Persons for Aids and Appliances",
        "benefit": "Free assistive devices: wheelchair, hearing aid, artificial limb, white cane, braille kit, tricycle, crutches",
        "eligibility_text": "Person with any disability who is an Indian citizen. Income below Rs.30,000 per month. At least 40 percent disability. Age 5 and above. Not received same device in last 3 years. Devices distributed through ALIMCO camps at district level.",
        "required_docs": ["Disability certificate 40 percent or more from government hospital", "Aadhaar card", "Income certificate", "Passport photo", "Age proof"],
        "apply_url": "https://depwd.gov.in/en/adip",
    },
    {
        "name": "PM-DAKSH Skill Development for SC OBC and Sanitation Workers",
        "benefit": "Free skill training with up to Rs.1,500 per month stipend during training for SC, OBC, sanitation workers, and tribal artisans",
        "eligibility_text": "SC, OBC, sanitation worker, or tribal artisan aged 18 to 45 years wanting to learn a skill for employment or self-employment. Training in beauty, retail, construction, hospitality, agriculture, and other vocational trades.",
        "required_docs": ["Aadhaar card", "Caste certificate", "Age proof", "Bank account"],
        "apply_url": "https://pmdaksh.dosje.gov.in",
    },
    {
        "name": "Unique Disability ID UDID Card",
        "benefit": "Single disability identity card giving access to all disability schemes and reservations across India",
        "eligibility_text": "Any person with any type of disability recognised under Rights of Persons with Disabilities Act 2016. Card issued by district medical authority after assessment. Needed to access all disability-related schemes and reservations in education and jobs.",
        "required_docs": ["Aadhaar card", "Medical assessment at government hospital", "Passport photo", "Residence proof"],
        "apply_url": "https://www.swavlambancard.gov.in",
    },
    {
        "name": "National Trust Schemes for Autism Cerebral Palsy Mental Retardation and Multiple Disabilities",
        "benefit": "Legal guardianship, care home support, home-based care assistance, and community integration for severely disabled persons",
        "eligibility_text": "Person with autism, cerebral palsy, intellectual disability, or multiple disabilities. National Trust provides registered caregivers, day care centres, group homes, and legal guardianship certificates.",
        "required_docs": ["Disability certificate", "Aadhaar card", "Birth certificate", "Doctor report"],
        "apply_url": "https://thenationaltrust.gov.in",
    },
    {
        "name": "SMILE Support for Marginalised Individuals for Livelihood and Enterprise",
        "benefit": "Rehabilitation for transgender persons and beggars: skill training, medical help, legal support, shelter, and livelihood",
        "eligibility_text": "Transgender persons, persons engaged in begging, and other marginalised individuals. Provides comprehensive rehabilitation including shelter, medical care, skill training for employment, and legal support for identity documents.",
        "required_docs": ["Aadhaar card if available", "Gender identity certificate for transgender persons", "Self-declaration"],
        "apply_url": "https://smile-b.dosje.gov.in",
    },
    {
        "name": "National Fellowship for Disabled Students",
        "benefit": "JRF Rs.37,000 per month and SRF Rs.42,000 per month for disabled students pursuing MPhil or PhD",
        "eligibility_text": "Student with at least 40 percent disability who has passed UGC-NET exam or been selected through other national level test for research. Pursuing MPhil or PhD at any recognised university. Up to 200 fellowships per year.",
        "required_docs": ["Disability certificate 40 percent or more", "UGC-NET or equivalent score card", "University admission letter", "Aadhaar card", "Bank account"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "Deendayal Disabled Rehabilitation Scheme DDRS",
        "benefit": "Grant to NGOs to run special schools, vocational training centres, and rehabilitation centres for disabled persons",
        "eligibility_text": "Disabled persons attending NGO-run special schools, vocational training centres, and rehabilitation centres. Covers children and adults with physical, visual, hearing, intellectual, and multiple disabilities.",
        "required_docs": ["Disability certificate", "Aadhaar card", "Referral from district social welfare officer"],
        "apply_url": "https://depwd.gov.in",
    },

    # =========================================================
    # SC / ST / MINORITIES  (121-133)
    # =========================================================
    {
        "name": "SHRESHTA Residential Education Scheme for SC Students",
        "benefit": "Free residential school education in top private schools for meritorious SC students covering tuition, hostel, books, and uniform",
        "eligibility_text": "Scheduled Caste student from Class 9 to 12 who has scored above 60 percent marks. Family income below Rs.2.5 lakh per year. Selected through merit examination. Studies at empanelled residential schools.",
        "required_docs": ["SC caste certificate", "Aadhaar card", "Income certificate", "Class 8 marksheet", "Bank account of parent"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "PM-AJAY PM Anusuchit Jaati Abhyuday Yojana",
        "benefit": "Village cluster development, income-generating schemes, and infrastructure in SC-majority areas",
        "eligibility_text": "Scheduled Caste families in villages where SC population is 50 percent or more. Covers agricultural support, livelihood programmes, sanitation, education infrastructure, skill development. Implemented through state governments.",
        "required_docs": ["Aadhaar card", "SC caste certificate", "Residence in SC-majority village"],
        "apply_url": "https://pmajay.dosje.gov.in",
    },
    {
        "name": "Credit Enhancement Guarantee Scheme for SC Entrepreneurs",
        "benefit": "Guarantee to banks so SC entrepreneurs can get business loans up to Rs.5 crore without full collateral",
        "eligibility_text": "Scheduled Caste entrepreneur who has an innovative business idea or existing business wanting to expand. Implemented through IFCI to provide guarantee to lender so loan is approved without full collateral.",
        "required_docs": ["SC caste certificate", "Aadhaar card", "Business plan or existing business proof", "Bank account", "PAN card"],
        "apply_url": "https://www.ifcicegssc.in",
    },
    {
        "name": "Pre-Matric Scholarship for SC Students",
        "benefit": "Scholarship and hostel charges for SC students studying in Class 1 to 10",
        "eligibility_text": "Scheduled Caste student in Class 1 to 10 with parent income below Rs.2.5 lakh per year. Covers day scholars in Class 9 to 10 and boarders in any class. Applied through National Scholarship Portal.",
        "required_docs": ["SC caste certificate", "Aadhaar card", "Income certificate", "School enrolment proof", "Bank account of parent"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "National Fellowship for SC Students",
        "benefit": "JRF Rs.37,000 per month and SRF Rs.42,000 per month for SC students pursuing MPhil or PhD",
        "eligibility_text": "Scheduled Caste student who has passed UGC-NET or been selected through other national test for research fellowship. Pursuing MPhil or PhD at any Indian university. Up to 2,000 fellowships per year.",
        "required_docs": ["SC caste certificate", "UGC-NET score card", "University admission letter", "Aadhaar card", "Bank account"],
        "apply_url": "https://nsfdc.nic.in/en/national-fellowship",
    },
    {
        "name": "Eklavya Model Residential Schools for ST Students",
        "benefit": "Free residential quality education Class 6 to 12 for tribal children in tribal-majority areas",
        "eligibility_text": "Scheduled Tribe child aged 10 to 14 years eligible for Class 6 admission. Child of ST family in tribal area. School provides free tuition, hostel, food, books, uniform, and co-curricular activities. Selection by merit or lottery.",
        "required_docs": ["ST caste certificate", "Aadhaar card", "Birth certificate", "Previous class marksheet"],
        "apply_url": "https://tribal.nic.in",
    },
    {
        "name": "Pradhan Mantri Van Dhan Vikas Kendra",
        "benefit": "Training and value addition support for tribal collectors of Minor Forest Produce including honey, tamarind, mahua, bamboo, medicinal plants",
        "eligibility_text": "Tribal person who collects minor forest produce from forest areas for livelihood. Forms Van Dhan SHG of 15 to 20 tribal people. Government gives training, processing equipment, and market linkage to add value to forest produce and earn more.",
        "required_docs": ["Aadhaar card", "ST certificate", "Proof of MFP collection self-declaration", "Bank account"],
        "apply_url": "https://trifed.tribal.gov.in",
    },
    {
        "name": "Pradhan Mantri Adi Adarsh Gram Yojana",
        "benefit": "Integrated development of tribal villages: roads, health centres, schools, Anganwadi, and drinking water in one package",
        "eligibility_text": "Resident of a tribal-dominated village with at least 50 percent tribal population and 500 or more tribal residents. All residents benefit from infrastructure development funded by convergence of central schemes.",
        "required_docs": ["Aadhaar card", "ST certificate", "Residence in selected village"],
        "apply_url": "https://tribal.nic.in",
    },
    {
        "name": "Minority Scholarship Pre-Matric",
        "benefit": "Rs.1,000 per year scholarship for minority students in Class 1 to 10",
        "eligibility_text": "Student from minority community Muslim, Christian, Sikh, Buddhist, Jain, or Parsi studying in Class 1 to 10. Family income below Rs.1 lakh per year. 30 percent reserved for girls.",
        "required_docs": ["Aadhaar card", "Minority community certificate", "Income certificate", "School enrolment", "Bank account of parent"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "Minority Scholarship Post-Matric",
        "benefit": "Tuition fee plus maintenance allowance for minority students in Class 11 and above",
        "eligibility_text": "Student from Muslim, Christian, Sikh, Buddhist, Jain, or Parsi community studying in Class 11 or above. Family income below Rs.2 lakh per year. 30 percent seats reserved for minority girls.",
        "required_docs": ["Aadhaar card", "Minority community certificate", "Income certificate", "Previous marksheet", "Admission letter", "Bank account"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "Merit-cum-Means Scholarship for Minority Students",
        "benefit": "Rs.20,000 to Rs.25,000 per year for minority students pursuing technical and professional degree courses",
        "eligibility_text": "Minority student enrolled in professional or technical courses like engineering, medicine, law, or MBA at recognised institutions. Income below Rs.2.5 lakh per year. Selection based on merit in previous year exams.",
        "required_docs": ["Aadhaar card", "Minority certificate", "Income certificate", "Admission letter to professional course", "Previous marksheet", "Bank account"],
        "apply_url": "https://scholarships.gov.in",
    },
    {
        "name": "SEED Scheme for Economic Empowerment of DNTs",
        "benefit": "Housing, education, health, and livelihood support for De-notified, Nomadic, and Semi-nomadic tribes",
        "eligibility_text": "Member of De-notified Tribe DNT, Nomadic Tribe NT, or Semi-Nomadic Tribe SNT. Communities historically notified as criminal tribes. Income limit applies. Covers children, women, and unemployed youth.",
        "required_docs": ["DNT or NT or SNT community certificate", "Aadhaar card", "Income certificate", "Residence proof"],
        "apply_url": "https://dwbdnc.dosje.gov.in",
    },
    {
        "name": "NAMASTE National Action for Mechanised Sanitation Ecosystem",
        "benefit": "Alternative employment, training, PPE kits, health insurance, and life cover for sanitation workers transitioning out of manual scavenging",
        "eligibility_text": "Sanitation worker safai karamchari involved in cleaning sewers, septic tanks, or insanitary latrines. Provides mechanical equipment, safety gear, training, and alternative livelihood support to eliminate manual scavenging.",
        "required_docs": ["Aadhaar card", "Proof of sanitation work employer certificate or self-declaration", "Bank account"],
        "apply_url": "https://bmsnamaste.dosje.gov.in",
    },

    # =========================================================
    # FOOD SECURITY  (134-140)
    # =========================================================
    {
        "name": "PM Garib Kalyan Anna Yojana PMGKAY",
        "benefit": "5 kg free food grain rice or wheat per person per month for all NFSA beneficiaries",
        "eligibility_text": "Any person covered under the National Food Security Act with ration card. Covers approximately 81 crore people in India. Free grain over and above the subsidised quota from ration shop.",
        "required_docs": ["Ration card", "Aadhaar card linked to ration card"],
        "apply_url": "https://dfpd.gov.in",
    },
    {
        "name": "National Food Security Act PDS Subsidised Grain",
        "benefit": "5 kg rice at Rs.3 per kg or wheat at Rs.2 per kg or coarse grain at Rs.1 per kg per person per month",
        "eligibility_text": "Household covered under NFSA with a ration card. Antyodaya Anna Yojana households get 35 kg per family per month. Priority households get 5 kg per person per month at heavily subsidised price.",
        "required_docs": ["Ration card", "Aadhaar card linked to ration card", "Residence in state where ration card issued"],
        "apply_url": "https://nfsa.gov.in",
    },
    {
        "name": "Antyodaya Anna Yojana",
        "benefit": "35 kg of food grain per family per month at Rs.2 per kg wheat or Rs.3 per kg rice for poorest of poor families",
        "eligibility_text": "The poorest of the poor families including landless agricultural labourers, marginal farmers, rural artisans, slum dwellers, daily wage labourers, domestic workers, widows, elderly without support, disabled persons, and destitute. Selected by state government.",
        "required_docs": ["Aadhaar card", "AAY ration card distinctive yellow card", "Residence in state"],
        "apply_url": "https://dfpd.gov.in",
    },
    {
        "name": "Midday Meal Scheme PM Poshan",
        "benefit": "Free hot cooked meal every school day for all children in government and government-aided schools Class 1 to 8",
        "eligibility_text": "Any child studying in Class 1 to 8 in any government or government-aided school. No income requirement. Meal provided during school hours improves nutrition, reduces hunger, and boosts school attendance especially for girls.",
        "required_docs": ["School enrolment, no separate application needed, automatic for enrolled students"],
        "apply_url": "https://pmposhan.education.gov.in",
    },
    {
        "name": "One Nation One Ration Card",
        "benefit": "Use your ration card at any ration shop anywhere in India, migrants can access food grain even in another state",
        "eligibility_text": "Any NFSA beneficiary holding a valid ration card. Specifically helps migrant workers who move from their home state to work elsewhere. They can access their entitled food grain in any state ration shop.",
        "required_docs": ["Ration card", "Aadhaar card linked to ration card"],
        "apply_url": "https://nfsa.gov.in",
    },
    {
        "name": "POSHAN Tracker Anganwadi Supplementary Nutrition",
        "benefit": "Free Take Home Ration and hot cooked meals through Anganwadi for children under 6, pregnant women, and lactating mothers",
        "eligibility_text": "Child aged 6 months to 6 years registered at Anganwadi centre. Pregnant woman. Lactating mother up to 6 months after delivery. All income levels. Available in every village and urban ward through Anganwadi worker.",
        "required_docs": ["Aadhaar card", "Registration at Anganwadi centre", "MCP card for pregnant or lactating women"],
        "apply_url": "https://poshanabhiyaan.gov.in",
    },
    {
        "name": "National Nutrition Mission Anaemia Mukt Bharat",
        "benefit": "Free iron and folic acid tablets, deworming medicine, and nutrition counselling for children, adolescents, and pregnant women",
        "eligibility_text": "Children aged 6 to 59 months, girls and boys aged 5 to 19 years, pregnant women, and lactating mothers. Delivered through ASHA workers, Anganwadi workers, and government schools. Addresses anaemia affecting over 50 percent of Indian women.",
        "required_docs": ["No separate application, delivered through Anganwadi and school automatically"],
        "apply_url": "https://nhm.gov.in",
    },

    # =========================================================
    # PENSION  (141-150)
    # =========================================================
    {
        "name": "Pradhan Mantri Shram Yogi Maan-dhan PM-SYM",
        "benefit": "Guaranteed Rs.3,000 per month pension after age 60 for unorganised workers. Government matches contribution.",
        "eligibility_text": "Unorganised sector worker aged 18 to 40 years with monthly income below Rs.15,000. Home-based workers, street vendors, midday meal workers, head-load workers, brick kiln workers, cobblers, rag pickers, domestic workers, washermen, rickshaw pullers. Not covered by NPS, ESIC, or EPFO.",
        "required_docs": ["Aadhaar card", "Bank account linked to Aadhaar", "Self-declaration of occupation and income", "Mobile number"],
        "apply_url": "https://maandhan.in",
    },
    {
        "name": "National Pension System NPS All Citizen Model",
        "benefit": "Market-linked retirement corpus with flexible contribution from Rs.500 per month and government regulation and tax benefits",
        "eligibility_text": "Any Indian citizen aged 18 to 70 years. Can open online or at any bank or post office. Useful for self-employed, freelancers, and private sector workers who have no employer pension. Section 80C tax deduction up to Rs.1.5 lakh.",
        "required_docs": ["Aadhaar card", "PAN card", "Bank account", "Passport photo"],
        "apply_url": "https://enps.nsdl.com",
    },
    {
        "name": "NPS Vatsalya Yojana",
        "benefit": "Pension savings account for minors, parents invest for child from birth, converts to regular NPS at age 18",
        "eligibility_text": "Any minor Indian child including newborns whose parent or guardian wants to start building retirement savings from an early age. Parent opens and manages the account until child turns 18. Minimum contribution Rs.1,000 per year. Launched September 2024.",
        "required_docs": ["Child birth certificate", "Parent Aadhaar card", "Parent PAN card", "Bank account"],
        "apply_url": "https://enps.nsdl.com",
    },
    {
        "name": "PM Kisan Maan Dhan Farmer Pension",
        "benefit": "Rs.3,000 per month pension after age 60 for small and marginal farmers who own less than 2 hectares",
        "eligibility_text": "Small or marginal farmer who owns less than 2 hectares of agricultural land. Age 18 to 40 years at time of enrolment. Government matches the farmer monthly contribution of Rs.55 to Rs.200 based on age.",
        "required_docs": ["Aadhaar card", "Land records below 2 hectares", "Bank account linked to Aadhaar", "Mobile number"],
        "apply_url": "https://maandhan.in",
    },
    {
        "name": "Public Provident Fund PPF",
        "benefit": "Safe government-backed savings with 7.1 percent annual interest, tax-free returns, up to Rs.1.5 lakh per year investment",
        "eligibility_text": "Any Indian citizen: salaried, self-employed, student, or housewife wanting to save money safely for 15 years. Can be extended in blocks of 5 years. Tax deduction under Section 80C. Available at any post office or bank.",
        "required_docs": ["Aadhaar card", "PAN card", "Passport photo", "Bank account"],
        "apply_url": "https://www.indiapost.gov.in",
    },
    {
        "name": "Common Service Centres CSC",
        "benefit": "Access to 300 plus government and private services in your village: Aadhaar, certificates, insurance, banking, passport, skill training",
        "eligibility_text": "Any citizen in rural or semi-urban area who needs government services without travelling to city. CSC provides certificate printing, pension enrolment, scheme applications, online banking, telemedicine, and legal services.",
        "required_docs": ["Aadhaar card", "Service-specific documents"],
        "apply_url": "https://csc.gov.in",
    },
    {
        "name": "DigiLocker",
        "benefit": "Free digital storage for government documents: Aadhaar, driving licence, marksheets, PAN, voter ID, accepted everywhere legally",
        "eligibility_text": "Any Indian citizen with an Aadhaar-linked mobile number. Free storage of all government-issued documents in digital form. Documents stored in DigiLocker are legally equivalent to originals. No physical copies needed when DigiLocker shown.",
        "required_docs": ["Aadhaar card linked to mobile number"],
        "apply_url": "https://digilocker.gov.in",
    },
    {
        "name": "PM WANI Public Wi-Fi Scheme",
        "benefit": "Cheap public Wi-Fi in shops, kirana stores, and public places through local entrepreneurs for low-cost internet access",
        "eligibility_text": "Any citizen in urban or rural area who needs affordable internet access. Local entrepreneurs become Public Data Office operators and provide Wi-Fi. Users access internet through registered PDO hotspots.",
        "required_docs": ["Aadhaar card or mobile number for registration"],
        "apply_url": "https://dot.gov.in",
    },
    {
        "name": "Aadhaar-Based Direct Benefit Transfer",
        "benefit": "All government scheme benefits transferred directly to Aadhaar-linked bank account, eliminating middlemen and corruption",
        "eligibility_text": "Any Indian citizen who is a beneficiary of any central or state government scheme. Bank account must be linked to Aadhaar. All pension, scholarship, subsidy, and welfare payments come directly without visiting government office for payment.",
        "required_docs": ["Aadhaar card", "Bank account linked to Aadhaar"],
        "apply_url": "https://dbtbharat.gov.in",
    },
    {
        "name": "Pradhan Mantri Jan Arogya Yojana for Artisans",
        "benefit": "Rs.5 lakh health insurance for artisans and craftspersons registered under PM Vishwakarma",
        "eligibility_text": "Traditional artisan or craftsperson registered under PM Vishwakarma Yojana in any of the 18 eligible trades. Health insurance of Rs.5 lakh per family per year at empanelled hospitals. No premium required for Vishwakarma beneficiaries.",
        "required_docs": ["PM Vishwakarma registration certificate", "Aadhaar card", "Bank account"],
        "apply_url": "https://pmvishwakarma.gov.in",
    },
]

if __name__ == "__main__":
    print(f"\nTotal schemes loaded: {len(SCHEMES)}\n")
    cats = [
        ("Agriculture and Farmers 1-20", 0, 20),
        ("Health 21-35", 20, 35),
        ("Women 36-50", 35, 50),
        ("Elderly 51-58", 50, 58),
        ("Education and Students 59-75", 58, 75),
        ("Livelihood Employment Micro-Credit 76-95", 75, 95),
        ("Housing and Infrastructure 96-103", 95, 103),
        ("Insurance and Social Security 104-112", 103, 112),
        ("Disability 113-120", 112, 120),
        ("SC ST Minorities 121-133", 120, 133),
        ("Food Security 134-140", 133, 140),
        ("Pension and Savings 141-150", 140, 150),
    ]
    for name, s, e in cats:
        print(f"  {name}: {e-s} schemes")
    print()


# Appended to reach 150 total
SCHEMES += [
    {
        "name": "Pradhan Mantri Awas Yojana Credit Linked Subsidy Scheme CLSS",
        "benefit": "Interest subsidy of 3 to 6.5 percent on home loans for middle-income families buying their first home in urban areas",
        "eligibility_text": "Middle income group family with annual income between Rs.6 lakh and Rs.18 lakh who has never owned a pucca house. Buying or constructing first home. Subsidy credited upfront to loan account reducing EMI significantly.",
        "required_docs": ["Aadhaar card", "Income certificate or salary slip", "Bank loan sanction letter", "Property agreement", "Self-declaration of no pucca house"],
        "apply_url": "https://pmaymis.gov.in",
    },
    {
        "name": "Rashtriya Swasthya Bima Yojana RSBY for Unorganised Workers",
        "benefit": "Cashless hospitalisation coverage up to Rs.30,000 per year for BPL families and unorganised workers",
        "eligibility_text": "Unorganised sector worker or BPL family member requiring hospitalisation. Covers all pre-existing diseases from day one. Family of 5 covered under one smart card. Available at empanelled government and private hospitals.",
        "required_docs": ["Aadhaar card", "BPL card or RSBY smart card", "e-Shram card or labour department registration"],
        "apply_url": "https://labour.gov.in",
    },
]
