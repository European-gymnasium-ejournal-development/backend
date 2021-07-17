from fpdf import FPDF
import datetime


date_today = "Prepared: " + str(datetime.datetime.now().strftime("%Y-%m-%d")) 
date_from_sign = "01.03.2021"
date_from = "From: " + "01.03.2021"
date_to_sign = "23.03.2021"
date_to = "To: " +  "23.03.2021"
marks_param = "ALLMARKS"
student_name = "Mark Temchenko"
grade = "Grade 9"
account_name = "Alexandra Manukian"
comment = "Tidewater goby baikal oilfish: hatchetfish sand eel ocean sunfish gombessa crocodile shark. Sacramento blackfish tope, bonito monkeyface prickleback, Bitterling greeneye. Inconnu: earthworm eel gray mullet airsac catfish Atlantic silverside mosshead warbonnet? Oriental loach Black triggerfish, warmouth yellowbelly tail catfish elephant fish. Featherback barramundi river shark Reef triggerfish European eel. Hoki, Steve fish haddock slimy sculpin, pink salmon beaked sandfish. Grouper Siamese fighting fish zingel Death Valley pupfish fierasfer; dusky grouper mahseer, longfin smelt gopher rockfish deep sea bonefish. Grunt sculpin rivuline sixgill shark gray eel-catfish croaker. Pikehead Rainbow trout Sacramento blackfish x-ray tetra flier, gouramie; long-finned pike flagfin morwong, skate grunter titan triggerfish. Channel catfish hagfish zebra bullhead shark pipefish morid cod. Yellowfin cutthroat trout, goby Antarctic icefish, mako shark. Electric ray knifefish nurseryfish salmon shark, bull shark swampfish Black sea bass. Longjaw mudsucker muskellunge hillstream loach tonguefish featherback summer flounder gombessa Red whalefish South American darter lionfish pike characid Arctic char. Pompano yellow jack Oregon chub; Lost River sucker halibut anglerfish pikeblenny; Sevan trout fierasfer Pacific trout orbicular batfish flatfish blue danio tilefish collared dogfish. Righteye flounder black bass antenna codlet spiny basslet prowfish scaleless black dragonfish boarfish Rabbitfish Black mackerel cutlassfish hawkfish yellow-edged moray cepalin."
subjects = ["Math", "English", "Aaaaaaa", "Bbbbbbbbbb", "Ggggggggggggg", "AoaAoaOAaoAOAOoAO"]

table_subject = "Math 9 Grade"
sign = student_name + " | " + grade + " | " + date_from_sign + "-" + date_to_sign + " | " + account_name + " | "
sign_test = sign + table_subject #table_subject вписал тут, но у тебя скорее всего он крутиться будет в for. Поэтому оставь sign тут, а в for прикручивай название предмета

def create_pdf(image_path, date_today, date_from, date_to, marks_param, student_name, grade, account_name, comment, subjects):
    pdf = FPDF()
    #1 страничка
    
    pdf.add_page()
    pdf.image(image_path, x=10, y=12, w=50) # Добавил логотип
    
    pdf.set_font("Arial", size=18)
    pdf.set_text_color(0, 102, 159)
    pdf.cell(290, 10, txt="European Gymnasium", ln=1, align="C") 
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=14)
    pdf.cell(275, 8, date_today,0,1,'C')
    pdf.cell(266, 1, date_from,0,1,'C')
    pdf.cell(260, 10, date_to,0,1,'C')
    pdf.cell(112, 1, "",0,0,'L')
    pdf.cell(30, 1, marks_param,0,1,'L')# Добавил Надписи справа от логотипа
    
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
    pdf.line(19, 94, 200, 94) #Добавил шапку с полосками
    
    pdf.set_font("Arial", size=15)
    pdf.cell(32, -37, "Comments:",0,1,'R')
    pdf.set_font("Arial", size=11)
    pdf.cell(13, 26, "",0,1,'R')
    pdf.multi_cell(190, 6, comment,0,1,'L') #Добавил комментарии
    
    #2 страничка
    pdf.add_page()
    pdf.set_font("Arial", size=15)
    pdf.cell(9, 0, txt="", ln=0, align="L")
    pdf.cell(0, 10, txt="List Of Subjects:", ln=1, align="L") #Добавил титульную надпись
    
    pdf.set_draw_color(0, 102, 159)
    pdf.set_line_width(0.5)
    pdf.line(23, 25, 190, 25)
    pdf.set_line_width(0.2) #Нарисовал жирную верхнюю полоску и задал ширину поменьше
    
    y_sub = 29 # Задал начальную высоту написания предмета
    y_line = 37 # Задал начальную высоту написания линии 
    y_tch = 33 # Задал начальную высоту написания учителя
    for subject in subjects:
        teacher = "Kuklin Markov" #Здесь вставляешь функцию поиска учителя по предмету
        
        pdf.set_text_color(0, 102, 159)
        pdf.set_font("Arial", size=11) #Параметры для надписи предмета
        
        pdf.set_xy(24,y_sub)
        pdf.cell(0, 0, subject, ln=1, align="L") #Задаю позицию курсора по статичному x и y из y_sub. Затем пишу название предмета
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=9) #Параметры для написания учителя
        
        pdf.set_xy(24,y_tch) 
        pdf.cell(0, 0, teacher, ln=1, align="L") #Задаю позицию курсора по статичному x и y из y_tch. Затем пишу учителя привязанного к предмету

        pdf.line(23, y_line, 190, y_line) #Рисую линию по статичному x и длинне, за высоту беру y_line
        
        y_line = y_line + 12
        y_sub = y_sub + 12
        y_tch = y_tch + 12 #Добавляю 12 к каждому параметру высоту, чтобы они аккуратно сместились вниз
        
    pdf.set_line_width(0.5)
    y_line = y_line - 12
    pdf.line(23, y_line, 190, y_line) #Рисую нижнюю жирную полоску. Отнимаю значение от высоты линии, чтобы она не съехала на деление вниз

    #3 страничка
    pdf.add_page()
    
    pdf.line(10, 7, 200, 7) #Верхняя линия
    
    pdf.cell(200, 0, sign_test, ln=1, align="C") # Контикул
    
    pdf.line(10, 13, 200, 13) #Нижняя линия

    
    


    pdf.output("simple_demo1.pdf")

if __name__ == '__main__':
    create_pdf('icon.png', date_today, date_from, date_to, marks_param, student_name, grade, account_name, comment, subjects)
