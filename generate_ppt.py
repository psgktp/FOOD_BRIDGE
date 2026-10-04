import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333) # 16:9 widescreen format
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout

    # Color Palette
    DARK_NAVY = RGBColor(15, 23, 42)      # #0f172a
    EMERALD = RGBColor(16, 185, 129)      # #10b981
    TEAL = RGBColor(6, 182, 212)          # #06b6d4
    LIGHT_BG = RGBColor(248, 250, 252)    # #f8fafc
    WHITE = RGBColor(255, 255, 255)
    SLATE_TEXT = RGBColor(51, 65, 85)     # #334155
    MUTED_TEXT = RGBColor(100, 116, 139)  # #64748b
    CARD_BORDER = RGBColor(226, 232, 240) # #e2e8f0
    ACCENT_GOLD = RGBColor(245, 158, 11)  # #f59e0b

    def set_slide_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_card(slide, left, top, width, height, bg_color=WHITE, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    def add_header(slide, tag_text, title_text, subtitle_text=None, is_dark=False):
        # Tag Badge
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p_tag = tf.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.bold = True
        p_tag.font.size = Pt(11)
        p_tag.font.color.rgb = EMERALD if is_dark else RGBColor(5, 150, 105)

        # Title
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.bold = True
        p_title.font.size = Pt(24)
        p_title.font.color.rgb = WHITE if is_dark else DARK_NAVY

        if subtitle_text:
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle_text
            p_sub.font.size = Pt(12)
            p_sub.font.color.rgb = MUTED_TEXT if not is_dark else RGBColor(148, 163, 184)

    # =========================================================================
    # SLIDE 1: Title Slide (Dark Theme, High Impact)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, DARK_NAVY)

    # Decorative glow card
    add_card(s1, Inches(0.8), Inches(1.2), Inches(11.733), Inches(5.1), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))

    tbox1 = s1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(11.0), Inches(4.2))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True

    p1 = tf1.paragraphs[0]
    p1.text = "🍱 FOODBRIDGE"
    p1.font.size = Pt(14)
    p1.font.bold = True
    p1.font.color.rgb = EMERALD

    p2 = tf1.add_paragraph()
    p2.text = "Autonomous Smart Food Rescue &\nNeed-Matching Logistics Platform"
    p2.font.size = Pt(32)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.space_before = Pt(8)

    p3 = tf1.add_paragraph()
    p3.text = "Hyperlocal Event-Aware Surplus Redistribution with Multi-Stage Chain-of-Custody Verification"
    p3.font.size = Pt(15)
    p3.font.color.rgb = RGBColor(148, 163, 184)
    p3.space_before = Pt(12)

    # Key highlight pills
    p4 = tf1.add_paragraph()
    p4.text = "⭐ 5 Signature Innovations  •  ⭐ N:1 Knapsack Pooling  •  ⭐ 4-Tier Urgency Decay  •  ⭐ Dual QR Handshake"
    p4.font.size = Pt(12)
    p4.font.bold = True
    p4.font.color.rgb = ACCENT_GOLD
    p4.space_before = Pt(24)

    p5 = tf1.add_paragraph()
    p5.text = "Web Technology Capstone Project  |  Python Flask + SQLAlchemy + GIS Heatmap"
    p5.font.size = Pt(12)
    p5.font.color.rgb = WHITE
    p5.space_before = Pt(18)

    # =========================================================================
    # SLIDE 2: Problem Statement & Literature Gap (Light Theme)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, LIGHT_BG)
    add_header(s2, "Context & Research Gap", "The Paradox of Institutional Food Waste", "Why conventional food listing apps fail in dense campus & urban environments")

    # Column 1: The Critical Problem
    add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), WHITE)
    tbox2_1 = s2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.6))
    tf2_1 = tbox2_1.text_frame
    tf2_1.word_wrap = True

    p = tf2_1.paragraphs[0]
    p.text = "🚨 The Operational Problem"
    p.font.bold = True
    p.font.size = Pt(17)
    p.font.color.rgb = RGBColor(220, 38, 38)

    bullets1 = [
        ("Bursty Campus Surplus", "Large edible surplus generated after college symposiums, hostel messes, banquet galas, and fests (50 to 500+ meals)."),
        ("Acute Food Insecurity", "Nearby orphanages, migrant worker shelters, and food banks struggle daily with chronic meal shortages."),
        ("Environmental Damage", "Decomposing food in landfills produces methane (CH4), causing 2.5x CO2e greenhouse gas impact per kg.")
    ]
    for title, desc in bullets1:
        p_b = tf2_1.add_paragraph()
        p_b.text = f"• {title}: {desc}"
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = SLATE_TEXT
        p_b.space_before = Pt(10)

    # Column 2: Limitations of Existing Systems
    add_card(s2, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0), WHITE)
    tbox2_2 = s2.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.2), Inches(4.6))
    tf2_2 = tbox2_2.text_frame
    tf2_2.word_wrap = True

    p = tf2_2.paragraphs[0]
    p.text = "⚠️ Limitations in Existing Solutions"
    p.font.bold = True
    p.font.size = Pt(17)
    p.font.color.rgb = DARK_NAVY

    bullets2 = [
        ("Static Directories & Ad-hoc WhatsApp", "Robin Hood Army / Food Banks rely on manual chatting, causing human latency and food spoilage."),
        ("Strict 1:1 Bottleneck (Olio / TGTG)", "Cannot handle cases where 1 shelter needs 200 meals, but 3 local donors only have 70+80+50 meals."),
        ("No Spoilage-Aware Urgency Timers", "Standard apps treat perishables like regular dry items without dynamic radius expansion."),
        ("Lack of Chain-of-Custody (CoC)", "No cryptographic handshake to verify handover, track safety, or indemnify donors.")
    ]
    for title, desc in bullets2:
        p_b = tf2_2.add_paragraph()
        p_b.text = f"• {title}: {desc}"
        p_b.font.size = Pt(11.5)
        p_b.font.color.rgb = SLATE_TEXT
        p_b.space_before = Pt(8)

    # =========================================================================
    # SLIDE 3: The 5 Signature Innovations & Architectural Pillars
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, LIGHT_BG)
    add_header(s3, "Core Technical Contributions", "The 5 Signature Engineering Pillars", "How FoodBridge provides an autonomous coordination layer instead of a basic directory")

    pillars = [
        ("1. Multi-Factor Match Engine", "Composite scoring formula balancing Haversine Distance (35%), Urgency Decay (30%), Org Capacity (20%), and Dietary Compatibility (15%).", RGBColor(16, 185, 129)),
        ("2. Multi-Donor N:1 Pooling", "Knapsack heuristic aggregating surplus from 3-4 small donors (e.g. 70 + 80 + 50 meals) into one unified 200-meal shelter delivery manifest.", RGBColor(245, 158, 11)),
        ("3. 4-Tier Urgency Decay", "Real-time clock: Green (>4h) -> Yellow (2-4h) -> Orange (1-2h) -> Red (<1h) with automated volunteer notification radius expansion.", RGBColor(239, 68, 68)),
        ("4. Campus Event Fast-Track", "1-Click surplus declaration for university fests, symposiums, and messes with instant student volunteer routing.", RGBColor(59, 130, 246)),
        ("5. Dual-Stage QR Handshake", "Two-step cryptographic verification at Donor Pickup (IN_TRANSIT) and NGO Handover (DELIVERED) for strict chain-of-custody.", RGBColor(147, 51, 234))
    ]

    # Render 3 top cards and 2 bottom cards
    card_w = Inches(3.64)
    card_h = Inches(2.2)

    # Top Row
    for idx in range(3):
        title, desc, accent = pillars[idx]
        c_left = Inches(0.8 + idx * 4.0)
        c_top = Inches(1.8)
        add_card(s3, c_left, c_top, card_w, card_h, WHITE)
        
        tb = s3.shapes.add_textbox(c_left + Inches(0.15), c_top + Inches(0.15), card_w - Inches(0.3), card_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.bold = True
        p_t.font.size = Pt(13)
        p_t.font.color.rgb = accent
        
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = SLATE_TEXT
        p_d.space_before = Pt(4)

    # Bottom Row
    card_w2 = Inches(5.6)
    card_h2 = Inches(2.2)
    for idx in range(2):
        title, desc, accent = pillars[3 + idx]
        c_left = Inches(0.8 + idx * 6.1)
        c_top = Inches(4.3)
        add_card(s3, c_left, c_top, card_w2, card_h2, WHITE)
        
        tb = s3.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.15), card_w2 - Inches(0.4), card_h2 - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.bold = True
        p_t.font.size = Pt(13)
        p_t.font.color.rgb = accent
        
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = SLATE_TEXT
        p_d.space_before = Pt(4)

    # =========================================================================
    # SLIDE 4: End-to-End System Workflow & Handshake Protocol
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, LIGHT_BG)
    add_header(s4, "System Operational Lifecycle", "End-to-End Coordination Workflow", "From surplus generation to verified recipient handover and ESG carbon accounting")

    steps = [
        ("Step 1: Surplus Posting", "Donor posts food via 1-Click Fast-Track with safe-use window.", "State: AVAILABLE"),
        ("Step 2: Smart Dispatch", "Engine computes Match Score & scans live GIS Demand Heatmap.", "State: MATCHING"),
        ("Step 3: NGO Claim / Pool", "Shelter accepts single batch or triggers N:1 Knapsack pooling.", "State: RESERVED"),
        ("Step 4: Volunteer Leg", "Active transport volunteer claims route on Leaflet interactive map.", "State: DISPATCHED"),
        ("Step 5: Pickup Handshake", "Volunteer scans Donor QR / OTP at canteen loading bay.", "State: IN_TRANSIT"),
        ("Step 6: Handover Complete", "NGO scans Delivery QR / OTP -> Impact Ledger records EPA CO2e.", "State: COMPLETED")
    ]

    for idx, (title, desc, state) in enumerate(steps):
        row = idx // 3
        col = idx % 3
        c_left = Inches(0.8 + col * 4.0)
        c_top = Inches(1.8 + row * 2.5)
        
        add_card(s4, c_left, c_top, Inches(3.7), Inches(2.2), WHITE)
        tb = s4.shapes.add_textbox(c_left + Inches(0.15), c_top + Inches(0.15), Inches(3.4), Inches(1.9))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p_num = tf.paragraphs[0]
        p_num.text = title
        p_num.font.bold = True
        p_num.font.size = Pt(13)
        p_num.font.color.rgb = DARK_NAVY
        
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = SLATE_TEXT
        p_d.space_before = Pt(4)
        
        p_s = tf.add_paragraph()
        p_s.text = f"📍 {state}"
        p_s.font.bold = True
        p_s.font.size = Pt(9.5)
        p_s.font.color.rgb = EMERALD
        p_s.space_before = Pt(6)

    # =========================================================================
    # SLIDE 5: Competitive Benchmarking & Verified Test Results
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, LIGHT_BG)
    add_header(s5, "Evaluation & Benchmark", "Competitive Matrix & Algorithm Test Results", "Proving technical novelty and system correctness over existing platforms")

    # Left: Benchmark Summary Card
    add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0), WHITE)
    tb5_1 = s5.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.6))
    tf5_1 = tb5_1.text_frame
    tf5_1.word_wrap = True

    p = tf5_1.paragraphs[0]
    p.text = "📊 Competitive Novelty Matrix"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = DARK_NAVY

    b_rows = [
        ("Olio / TGTG", "C2C / Retail sales only, no demand-side sensing or N:1 pooling."),
        ("Robin Hood Army", "Manual WhatsApp coordination, lacks real-time urgency & CoC."),
        ("Food Rescue Hero", "US corporate recurring routes, lacks campus event fast-track."),
        ("FoodBridge (Our Work)", "Combines N:1 Pooling + 4-Tier Decay + Event Fast-Track + Live GIS Heatmap + Dual QR Handshakes.")
    ]
    for name, note in b_rows:
        p_b = tf5_1.add_paragraph()
        p_b.text = f"• {name}: {note}"
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = SLATE_TEXT
        p_b.space_before = Pt(6)

    # Right: Verified Test Execution Metrics
    add_card(s5, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0), DARK_NAVY, border_color=None)
    tb5_2 = s5.shapes.add_textbox(Inches(7.1), Inches(2.0), Inches(5.2), Inches(4.6))
    tf5_2 = tb5_2.text_frame
    tf5_2.word_wrap = True

    p = tf5_2.paragraphs[0]
    p.text = "🧪 Verified Engine Test Results"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = EMERALD

    test_metrics = [
        ("Smart Match Precision", "Donation #1 matched Mercy Shelter Home at 94.3% (0.88 km) and Hope City at 92.7% (2.0 km)."),
        ("N:1 Knapsack Pooling", "For 200 meals deficit, pooled 120 (Tech Fest) + 50 (Hotel) + 30 (Mess) = 200 meals satisfied across 3 donors."),
        ("Dynamic Decay Clock", "Auto-computed 2.5h buffer remaining with High Urgency (Orange) visual badge."),
        ("Carbon Offset Calculation", "770 meals rescued = 308.0 kg biomass diverted = 770.0 kg CO2e greenhouse gas abated.")
    ]
    for metric, res in test_metrics:
        p_m = tf5_2.add_paragraph()
        p_m.text = f"✓ {metric}:\n  {res}"
        p_m.font.size = Pt(10.5)
        p_m.font.color.rgb = WHITE
        p_m.space_before = Pt(6)

    # =========================================================================
    # SLIDE 6: Tech Stack, Environmental Impact & Conclusion
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, LIGHT_BG)
    add_header(s6, "Implementation & Impact", "Technology Architecture & Future Scope", "Production-ready, database-agnostic full-stack implementation")

    # Box 1: Tech Stack
    add_card(s6, Inches(0.8), Inches(1.8), Inches(3.7), Inches(5.0), WHITE)
    tb6_1 = s6.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(3.3), Inches(4.6))
    tf6_1 = tb6_1.text_frame
    tf6_1.word_wrap = True
    
    p = tf6_1.paragraphs[0]
    p.text = "💻 Technology Stack"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = DARK_NAVY

    stack = [
        "Backend: Python 3.13, Flask, Werkzeug, Flask-Login",
        "Database: SQLAlchemy ORM (SQLite / PostgreSQL ready)",
        "GIS & Heatmap: Leaflet.js, OpenStreetMap, Leaflet.heat",
        "Handshake: QRCode (PIL), Base64 URI, Dual-OTP",
        "Frontend: Bootstrap 5, Inter Typography, Responsive UI"
    ]
    for item in stack:
        p_i = tf6_1.add_paragraph()
        p_i.text = f"• {item}"
        p_i.font.size = Pt(10.5)
        p_i.font.color.rgb = SLATE_TEXT
        p_i.space_before = Pt(6)

    # Box 2: Environmental & ESG Impact
    add_card(s6, Inches(4.8), Inches(1.8), Inches(3.7), Inches(5.0), WHITE)
    tb6_2 = s6.shapes.add_textbox(Inches(5.0), Inches(2.0), Inches(3.3), Inches(4.6))
    tf6_2 = tb6_2.text_frame
    tf6_2.word_wrap = True

    p = tf6_2.paragraphs[0]
    p.text = "🌱 Social & ESG Impact"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = EMERALD

    esg = [
        "Landfill Diversion: Reduces methane emissions by 2.5 kg CO2e per kg food saved.",
        "Campus Green Leaderboard: Quantifies university fest sustainability rankings.",
        "Good Samaritan Protection: Built-in food safety compliance checklists & audit logs.",
        "Zero-Waste Campuses: Enables colleges to achieve green institutional certifications."
    ]
    for item in esg:
        p_i = tf6_2.add_paragraph()
        p_i.text = f"• {item}"
        p_i.font.size = Pt(10.5)
        p_i.font.color.rgb = SLATE_TEXT
        p_i.space_before = Pt(6)

    # Box 3: Conclusion & Next Steps
    add_card(s6, Inches(8.8), Inches(1.8), Inches(3.7), Inches(5.0), DARK_NAVY, border_color=None)
    tb6_3 = s6.shapes.add_textbox(Inches(9.0), Inches(2.0), Inches(3.3), Inches(4.6))
    tf6_3 = tb6_3.text_frame
    tf6_3.word_wrap = True

    p = tf6_3.paragraphs[0]
    p.text = "🎯 Conclusion & Scope"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = ACCENT_GOLD

    future = [
        "Conclusion: FoodBridge proves that intelligent demand-matching & N:1 pooling dramatically cut food recovery latency.",
        "IoT Cold Chain: Future integration with BLE temperature probes for chilled storage tracking.",
        "Municipal Scale: Ready for pilot deployment across city campuses and food banks."
    ]
    for item in future:
        p_i = tf6_3.add_paragraph()
        p_i.text = f"• {item}"
        p_i.font.size = Pt(10.5)
        p_i.font.color.rgb = WHITE
        p_i.space_before = Pt(6)

    output_path = os.path.join(os.path.dirname(__file__), "FoodBridge_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == '__main__':
    create_presentation()
