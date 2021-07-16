from fpdf import FPDF
import datetime

date_today = "Prepared: " + str(datetime.datetime.now().strftime("%Y-%m-%d")) 
date_from = "From: " + "01.03.2021"
date_to = "To: " +  "23.03.2021"
marks_param = "ALLMARKS"
student_name = "Mark Temchenko"
grade = "Grade 9"
account_name = "Alexandra Manukian"
comment = "Tidewater goby baikal oilfish: hatchetfish sand eel ocean sunfish gombessa crocodile shark. Sacramento blackfish tope, bonito monkeyface prickleback, Bitterling greeneye. Inconnu: earthworm eel gray mullet airsac catfish Atlantic silverside mosshead warbonnet? Oriental loach Black triggerfish, warmouth yellowbelly tail catfish elephant fish. Featherback barramundi river shark Reef triggerfish European eel. Hoki, Steve fish haddock slimy sculpin, pink salmon beaked sandfish. Grouper Siamese fighting fish zingel Death Valley pupfish fierasfer; dusky grouper mahseer, longfin smelt gopher rockfish deep sea bonefish. Grunt sculpin rivuline sixgill shark gray eel-catfish croaker. Pikehead Rainbow trout Sacramento blackfish x-ray tetra flier, gouramie; long-finned pike flagfin morwong, skate grunter titan triggerfish. Channel catfish hagfish zebra bullhead shark pipefish morid cod. Yellowfin cutthroat trout, goby Antarctic icefish, mako shark. Electric ray knifefish nurseryfish salmon shark, bull shark swampfish Black sea bass. Longjaw mudsucker muskellunge hillstream loach tonguefish featherback summer flounder gombessa Red whalefish South American darter lionfish pike characid Arctic char. Pompano yellow jack Oregon chub; Lost River sucker halibut anglerfish pikeblenny; Sevan trout fierasfer Pacific trout orbicular batfish flatfish blue danio tilefish collared dogfish. Righteye flounder black bass antenna codlet spiny basslet prowfish scaleless black dragonfish boarfish Rabbitfish Black mackerel cutlassfish hawkfish yellow-edged moray cepalin."

def create_pdf(image_path, date_today, date_from, date_to, marks_param, student_name, grade, account_name, comment):
    pdf = FPDF()
    pdf.add_page()
    pdf.image(image_path, x=10, y=12, w=50)
    pdf.set_font("Arial", size=18)
    pdf.set_text_color(0, 102, 159)
    pdf.cell(290, 10, txt="European Gymnasium", ln=1, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=14)
    pdf.cell(275, 8, date_today,0,1,'C')
    pdf.cell(266, 1, date_from,0,1,'C')
    pdf.cell(260, 10, date_to,0,1,'C')
    pdf.cell(113, 1, "",0,0,'L')
    pdf.cell(30, 1, marks_param,0,1,'L')
    pdf.set_draw_color(0, 102, 159)
    pdf.set_line_width(0.5)
    pdf.line(19, 68, 200, 68)
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(0, 102, 159)
    pdf.cell(33, 65, "Student name: ",0,0,'R')
    pdf.set_text_color(0, 0, 0)
    pdf.cell(-14, 65, student_name,0,1,'L')
    pdf.set_line_width(0.2)
    pdf.line(19, 77, 200, 77)
    pdf.set_text_color(0, 102, 159)
    pdf.cell(20, -48, "Grade: ",0,0,'R')
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, -48, grade,0,1,'L')
    pdf.line(19, 85, 200, 85)
    pdf.set_text_color(0, 102, 159)
    pdf.cell(22, 65, "Advisor: ",0,0,'R')
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 65, account_name,0,1,'L')
    pdf.line(19, 94, 200, 94)
    pdf.set_font("Arial", size=15)
    pdf.cell(32, -37, "Comments:",0,1,'R')
    pdf.set_font("Arial", size=11)
    pdf.cell(13, 26, "",0,1,'R')
    pdf.multi_cell(190, 6, comment,0,1,'L')
   

    
    


    pdf.output("simple_demo1.pdf")

if __name__ == '__main__':
    create_pdf('icon.png', date_today, date_from, date_to, marks_param, student_name, grade, account_name, comment)
