"""The 15 government welfare schemes.

`eligibility_text` is written in PLAIN natural language (not bureaucratic jargon)
on purpose: it is the field we embed for vector search, so it must read the way a
real person describes their own life out loud. That is what makes the semantic
match work ("poor widow farmer" -> "BPL female cultivator with spousal bereavement").
"""

SCHEMES = [
    {
        "name": "PM Kisan Samman Nidhi",
        "benefit": "₹6,000 per year in 3 installments directly to bank account",
        "eligibility_text": "Small and marginal farmer who owns agricultural land. Any gender. Any Indian state. No income limit but land ownership required. Family must not have government job or pay income tax.",
        "required_docs": ["Aadhaar card", "Land ownership records (Khasra/Khatauni)", "Bank account passbook", "Mobile number"],
        "apply_url": "https://pmkisan.gov.in",
    },
    {
        "name": "Indira Gandhi National Widow Pension Scheme",
        "benefit": "₹300 per month pension (state may add more)",
        "eligibility_text": "Woman who has lost her husband. Age between 40 and 79 years. Must belong to Below Poverty Line (BPL) family. Rural or urban. Any state in India.",
        "required_docs": ["Husband's death certificate", "BPL card or ration card", "Aadhaar card", "Bank passbook", "Age proof"],
        "apply_url": "https://nsap.nic.in",
    },
    {
        "name": "Ayushman Bharat PM-JAY",
        "benefit": "₹5 lakh health insurance per family per year for hospital treatment",
        "eligibility_text": "Poor family listed in SECC 2011 database or BPL card holder. Covers all family members including elderly parents and children. No premium to pay. Cashless treatment at government and empanelled private hospitals.",
        "required_docs": ["Aadhaar card", "Ration card or BPL certificate", "Family ID"],
        "apply_url": "https://pmjay.gov.in",
    },
    {
        "name": "PM Awas Yojana Gramin",
        "benefit": "₹1.2 lakh grant (₹1.3 lakh in hilly areas) to build a pucca house",
        "eligibility_text": "Rural family living in kachha house (mud or thatch) or homeless. BPL family. Priority to SC/ST, widows, disabled, and families with no adult male member. Must not already own a pucca house.",
        "required_docs": ["BPL card", "Aadhaar card", "Bank passbook", "Land documents or site certificate", "Photo of current house"],
        "apply_url": "https://pmayg.nic.in",
    },
    {
        "name": "PM Ujjwala Yojana",
        "benefit": "Free LPG gas connection with cylinder and stove",
        "eligibility_text": "Woman from BPL family who does not already have an LPG connection in the household. Adult woman must be the applicant. Especially for women using wood or coal for cooking which causes indoor pollution.",
        "required_docs": ["Aadhaar card", "BPL card or ration card", "Bank passbook", "Passport photo"],
        "apply_url": "https://pmuy.gov.in",
    },
    {
        "name": "MGNREGA (Mahatma Gandhi National Rural Employment Guarantee)",
        "benefit": "100 days of guaranteed wage employment per year at minimum wage",
        "eligibility_text": "Any adult member of a rural household willing to do unskilled manual work. No income limit. Family must apply for a job card from Gram Panchayat. Works include digging wells, building roads, planting trees.",
        "required_docs": ["Aadhaar card", "Ration card", "Passport photo", "Bank passbook"],
        "apply_url": "https://nrega.nic.in",
    },
    {
        "name": "PM Fasal Bima Yojana",
        "benefit": "Crop insurance — compensation if crops fail due to flood, drought, pest, or natural disaster",
        "eligibility_text": "Any farmer who has taken a crop loan from a bank. Also voluntary for farmers without loans. Covers all food crops, oilseeds, and commercial crops. Premium is very low — government pays the rest.",
        "required_docs": ["Aadhaar card", "Land records", "Bank account", "Crop sowing certificate from Patwari"],
        "apply_url": "https://pmfby.gov.in",
    },
    {
        "name": "Indira Gandhi National Old Age Pension",
        "benefit": "₹200 per month (age 60-79) or ₹500 per month (age 80+) from central government. States add more.",
        "eligibility_text": "Elderly person aged 60 years or above. Must belong to BPL family. Any gender. Any state. Destitute person with little or no regular income. SC/ST elderly get priority.",
        "required_docs": ["Age proof (birth certificate or school certificate)", "BPL card", "Aadhaar card", "Bank passbook"],
        "apply_url": "https://nsap.nic.in",
    },
    {
        "name": "PM Matru Vandana Yojana",
        "benefit": "₹5,000 cash in 3 installments for first live birth",
        "eligibility_text": "Pregnant woman and lactating mother for her first living child. Must be 19 years or older. Registered at Anganwadi or health center. Cash transferred directly to bank account to compensate for wage loss during pregnancy.",
        "required_docs": ["Aadhaar card", "MCP card (Mother and Child Protection card)", "Bank passbook", "Mobile number"],
        "apply_url": "https://pmmvy.wcd.gov.in",
    },
    {
        "name": "Kisan Credit Card",
        "benefit": "Short-term credit up to ₹3 lakh at 4% interest rate for farming expenses",
        "eligibility_text": "Farmer, tenant farmer, sharecropper, or oral lessee. Also for self-help groups. Used to buy seeds, fertilizer, pesticides. Animal husbandry and fisheries farmers also eligible. Very low interest because government subsidizes it.",
        "required_docs": ["Aadhaar card", "Land documents or lease agreement", "Passport photo", "Application from bank"],
        "apply_url": "https://www.rbi.org.in/kisan-credit-card",
    },
    {
        "name": "PM SVANidhi (Street Vendor Micro Credit)",
        "benefit": "Collateral-free loan of ₹10,000 (first), ₹20,000 (second), ₹50,000 (third) for street vendors",
        "eligibility_text": "Urban street vendor or hawker. Must have vending certificate from Urban Local Body or letter of recommendation from Town Vending Committee. Fruit sellers, vegetable sellers, tea stall, cobbler, laundry, barber — all eligible.",
        "required_docs": ["Aadhaar card", "Vending certificate or ULB letter", "Bank passbook", "Mobile number linked to Aadhaar"],
        "apply_url": "https://pmsvanidhi.mohua.gov.in",
    },
    {
        "name": "Beti Bachao Beti Padhao",
        "benefit": "Sukanya Samriddhi account with high interest (8%+) for girl child's education and marriage",
        "eligibility_text": "Parents or guardian of a girl child under 10 years of age. Account opened in Post Office or bank. Maximum deposit ₹1.5 lakh per year. Matures when girl turns 21. Partial withdrawal allowed at 18 for education.",
        "required_docs": ["Girl child's birth certificate", "Parent Aadhaar card", "Parent PAN card", "Passport photo"],
        "apply_url": "https://wcd.nic.in/bbbp-schemes",
    },
    {
        "name": "PM Vishwakarma Yojana",
        "benefit": "₹15,000 toolkit grant + skill training + ₹1 lakh loan at 5% interest",
        "eligibility_text": "Traditional artisan or craftsperson working with hands and tools. Includes blacksmith, goldsmith, potter, carpenter, tailor, cobbler, barber, washerman, fishing net maker, and 12 other trades. Self-employed, not a salaried employee.",
        "required_docs": ["Aadhaar card", "Proof of trade or craft (photos, tools, references)", "Bank passbook", "Mobile number"],
        "apply_url": "https://pmvishwakarma.gov.in",
    },
    {
        "name": "Janani Suraksha Yojana",
        "benefit": "₹1,400 cash (rural) or ₹1,000 (urban) for institutional delivery at government hospital",
        "eligibility_text": "Pregnant woman from BPL family delivering at government hospital or accredited private hospital. Below poverty line women in all states. Above poverty line women in low-performing states like UP, Bihar, Rajasthan, MP, Jharkhand, Orissa.",
        "required_docs": ["Aadhaar card", "BPL card", "MCP card", "Hospital delivery record"],
        "apply_url": "https://nhm.gov.in/jsy",
    },
    {
        "name": "National Family Benefit Scheme",
        "benefit": "₹20,000 one-time lump sum payment to family when breadwinner dies",
        "eligibility_text": "Rural or urban BPL family where the primary earning member has died. Age of deceased must be 18 to 64 years. Death can be due to any cause. Applied within 90 days of death. Helps family survive immediate crisis after losing income earner.",
        "required_docs": ["Death certificate of breadwinner", "BPL card", "Aadhaar of applicant family member", "Bank passbook", "Proof of relationship"],
        "apply_url": "https://nsap.nic.in",
    },
]
