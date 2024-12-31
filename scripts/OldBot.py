import pdfplumber
import requests
import pandas as pd
import re
import urllib3
import io


class OldBot:
    def __init__(self, type, numJudges, numElems=12):
        self.programType = type
        self.txt = ""
        self.info = []
        self.allJumps = []
        self.bv = []
        self.totTes = []
        self.totPcs = []
        self.totS = []
        self.numJudges = numJudges
        self.numElems = numElems
        # if type == "short":
        #     self.numElems = 7
        # else:
        #     self.numElems = 12

    def extract(self, url):
        all_text = ''
        http = urllib3.PoolManager()
        temp = io.BytesIO()
        # temp.write(http.request("GET", url).data)
        temp.write(requests.get(url, verify=False).content)
        try:    # to verify is the url has valid pdf file!
            pdf = pdfplumber.open(temp)
            for pdf_page in pdf.pages:
                single_page_text = pdf_page.extract_text()
                # TypeError: can only concatenate str (not "NoneType") to str
                if single_page_text is not None: 
                    all_text += '\n' + single_page_text
            pdf.close()
        except:
            pass
        return all_text

    def download(self, url):
        filename = url.split("/")[-1]
        with requests.get(url) as r:
            with open(filename, "wb") as f:
                f.write(r.content)
        return filename

    def openFile(self):
        with pdfplumber.open(self.ap) as pdf:
            pgs = pdf.pages
            for i,pg in enumerate(pgs):
                self.txt += pg.extract_text() + "\n"

    def maxElementScore(self, df):
        s = df.copy()
        return (s['Score'].max())

    def style_max(self, df):
        #print(s.max(axis=1))
        #maxV = s['Score'].max()
        s = df.astype(float)
        is_max = s == s.max()
        return ['color: #008000' if v else '' for v in is_max] 

    def style_bonus(self, df):
        is_bonus = df[len(df) - 1] == "x"
        return ['color: #008000;font-weight: 500;' if v else '' for v in is_bonus] 
    def style_min(self, df):
        s = df.astype(float)
        is_min = s == s.min()
        return ['color:#BF0000;font-weight:500;' if v else '' for v in is_min]
    
    def styleFive(self,s):
        if int(s['J1']) == 5:
            return 'color:#637a47'
        else:
            return ''

    def neg(self, s):
        if float(s['GOE']) < 0 or '!' in s['Element']:
            return ['color:#BF0000'] * len(s)
        else:
            return [''] * len(s)


    def jumpData(self, data):
        # (self.info)
        skater = (str(self.info[0][0]) + " ") + str(self.info[0][1]) + " (" + str(self.info[0][2]).upper() + ")" 
        df = pd.DataFrame(data,
                          columns = pd.Index(['Element', 'Base Value', 'GOE', 'J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8', 'J9', 'Score'])) 
        
        
        df['Base Value'] = df['Base Value'].map('{:,.2f}'.format)
        df['GOE'] = df['GOE'].map('{:,.2f}'.format)
        df['J1'] = df['J1'].map('{:.0f}'.format)
        df['J2'] = df['J2'].map('{:.0f}'.format)
        df['J3'] = df['J3'].map('{:.0f}'.format)
        df['J4'] = df['J4'].map('{:.0f}'.format)
        df['J5'] = df['J5'].map('{:.0f}'.format)
        df['J6'] = df['J6'].map('{:.0f}'.format)
        df['J7'] = df['J7'].map('{:.0f}'.format)
        df['J8'] = df['J8'].map('{:.0f}'.format)
        df['J9'] = df['J9'].map('{:.0f}'.format)
        df['Score'] = df['Score'].map('{:,.2f}'.format)
        
        for i in range(len(df.index)):
            if (df.loc[i, "Base Value"])[len(df.loc[i, "Base Value"])-1] != "0":
                df.loc[i, "Base Value"] = df.loc[i, "Base Value"] + " x"
                

        df = df.style.apply(self.style_max, subset = 'Score', axis = 0)
        
        
        # df = df.style.applymap(self.styleFive)
        df = df.apply(self.neg, axis = 1)
        df = df.apply(lambda x: ['color:#008000; font-weight: 500;'
                          if (11 >= i >= 3 and (int(v) == 5) )
                          else "" for i, v in enumerate(x)], axis = 1)
        df = df.map(lambda x: 'color:#008000; font-weight: 500;'
                            if ( x[len(x)-1] == "x")
                            else "")                
        df = df.hide(axis='index')
        # print(self.info[0][7])
        df = df.set_caption(str(self.info[0][7] + "\t" + skater))
    
        return df

    def pcsData(self, data):
        l = data[0:5]
        # print(l)
        for j in range(len(l)):
            l[j] = l[j][1:]
        df = pd.DataFrame(l,
                           columns = pd.Index(['Component', 'Factor','J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8', 'J9', 'Total']))
        df['Factor'] = df['Factor'].map('{:,.2f}'.format)
        df['J1'] = df['J1'].map('{:,.2f}'.format)
        df['J2'] = df['J2'].map('{:.2f}'.format)
        df['J3'] = df['J3'].map('{:.2f}'.format)
        df['J4'] = df['J4'].map('{:.2f}'.format)
        df['J5'] = df['J5'].map('{:.2f}'.format)
        df['J6'] = df['J6'].map('{:.2f}'.format)
        df['J7'] = df['J7'].map('{:.2f}'.format)
        df['J8'] = df['J8'].map('{:.2f}'.format)
        df['J9'] = df['J9'].map('{:.2f}'.format)    
        df['Total'] = df['Total'].map('{:,.2f}'.format)    
        
        
        df = df.style.apply(self.style_max, subset = 'Total', axis = 0)
        df = df.apply(self.style_min, subset = 'Total', axis = 0)
        df = df.hide(axis='index')
        return df

    def tot(self, data):
        l = data[0]
        self.bv.append([l[0], float(l[1])])
        self.totTes.append([l[0], float(l[2])])
        self.totPcs.append([l[0], float(l[3])])
        l.append("Total Score: " + "{:.2f}".format(float(l[2]) + float(l[3]) + float(l[4])))
        self.totS.append([l[0], float(l[2]) + float(l[3]) + float(l[4])])
        l[1] = "TES BV: " + l[1]
        l[2] = "Total TES: " + l[2]  
        l[3] = "Total PCS: " + l[3]
        l[4] = "Deductions: " + l[4]
        l = l[1:]
        df = pd.DataFrame([l])
        df = df.style.hide(axis='index')
        return df
    
    def pcsRegex(self):
        regex = r"(Skating Skills|Transitions|Performance|Composition|Interpretation of the Music)\s{1,}([\d,]+\.\d{2})"
        for i in range(self.numJudges + 1):
            regex += r"\s{1,}([\d,]+\.\d{2})"
        return regex
    
    def elementRegex(self):
        regex = r"(\d{1,2})\s{1,}([\S]{1,})(?:[\s!q<enCS\*]*)\s{1,}([\d,]+\.\d{2})?(?:[\sxX\*]*)\s{1,}([\S]{1,}\.\d{2})"
        for i in range(self.numJudges):
            regex += r"\s{1,}([\s\S]{1,2})"
        regex += r"\s{1,}([\d,]+\.\d{2})"
        return regex

    
    def run(self, title, url, compName):
        # compName = url[url.rfind("/")-7:url.rfind("/")] + "_" + url[url.rfind("/") + 1:url.find("-")]

        cnt = 0
        curr = 0
        hL, n, nn, self.pcsL, lnIt, jumps, stsq, chsq, spin, tots= [], [] ,[], [], [], [], [] ,[], [], []

        self.txt = self.extract(url)
        # print(self.txt)
        # skaterRegex = re.compile(r"(\d{1,})\s{1,}([a-zA-Z]{1,}'?-?\s?[a-zA-Z]{1,}?)\s{1,}([a-zA-Z]{1,}'?-?[a-zA-Z]{1,}\s?[a-zA-Z]{1,}?)\s{1,}([A-Z]{3})\s{1,}(\d{1,})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([-]?[\d,]+\.\d{2})")
        # skaterRegex = re.compile(r"(\d{1,})\s{1,}([a-zA-Z]{1,}'?-?\s?[a-zA-Z]{1,}?)\s{1,}([a-zA-Z]{1,}'?-?\s?[a-zA-Z]{1,})\s{1,}([A-Z]{3})\s{1,}(\d{1,})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([-]?[\d,]+\.\d{2})")
        # skaterRegex = re.compile(r"(\d{1,})\s{1,}([a-zA-Z]{1,}'?-?\s?[a-zA-Z]{1,}?)\s{1,}([a-zA-Z]{1,}'?-?\s?[a-zA-Z]{1,}\s?[a-zA-Z]{1,}?)\s{1,}([A-Z]{3})\s{1,}(\d{1,})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([-]?[\d,]+\.\d{2})")
        skaterRegex = re.compile(r"(\d{1,})\s{1,}([a-zA-ZÀ-ÖØ-öø-ÿ]{1,}'?-?\s?[a-zA-ZÀ-ÖØ-öø-ÿ]{1,}?)\s{1,}([a-zA-ZÀ-ÖØ-öø-ÿ-'\s]{1,})\s{1,}([A-Z]{3})\s{1,}(\d{1,})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([-]?[\d,]+\.\d{2})")
        
        #elementRegex = re.compile(r'(\d{1,2})\s{1,}([\S]{1,})(?:[\s!q<enCS\*]*)\s{1,}([\d,]+\.\d{2})(?:[\sx\*]*)\s{1,}([\S]{1,}\.\d{2})\s{1,}([\s\S]{1,2})\s{1,}([\s\S]{1,2})\s{1,}([\s\S]{1,2})\s{1,}([\s\S]{1,2})\s{1,}([\s\S]{1,2})\s{1,}([\s\S]{1,2})\s{1,}([\s\S]{1,2})\s{1,}([\s\S]{1,2})\s{1,}([\s\S]{1,2})\s{1,}([\d,]+\.\d{2})')
        #pcsRegex = re.compile(r'(Skating Skills|Transitions|Performance|Composition|Interpretation of the Music)\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s{1,}([\d,]+\.\d{2})\s?([\d,]?+\.?\d{2}?)')
        
        pcsRegex = re.compile(self.pcsRegex())
        elementRegex = re.compile(self.elementRegex())
        progComp = re.compile(r'(Program Components\sFactor)')
        jtpcs = re.compile(r'(?:Judges Total Program Component Score \(factored\))\s{1,}([\d,]+\.\d{2})\s{1,}')

        for ln in self.txt.split("\n"):
            ln = skaterRegex.search(ln)
            if ln:
                place = ln.group(1)
                n1 = ln.group(3)
                n2 = ln.group(2)
                noc = ln.group(4)
                total = ln.group(6)
                tes = ln.group(7)
                pcs = ln.group(8)
                ded = ln.group(9)
                if n1.isupper():
                    frst = n2
                    last = n1
                else:
                    frst = n1
                    last = n2

                self.info.append([frst,last,noc, total, tes, pcs, ded, place])  
                for i in range(12): 
                    n.append([frst.capitalize() + ' ' + last.capitalize() ])
                nn.append([frst.capitalize() + ' ' + last.capitalize() ])

        print(nn)
        for ln in self.txt.split("\n"):
            pcsLn = pcsRegex.search(ln)
            if pcsLn:
                pc = pcsLn.group(1)
                if pc == "Interpretation of the Music":
                    pc = "Interpretation"
                factor = float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(2))))
                currLine = [nn[curr], pc, factor]

                for i in range(self.numJudges):
                    currLine.append(float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(i+3)))))
                for i in range(self.numJudges + 1, 10):
                    currLine.append(0.0)
                currLine.append(float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(self.numJudges+3)))))
                self.pcsL.append(currLine)

                # pcs1 = float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(3))))
                # pcs2 = float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(4))))
                # pcs3 = float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(5))))
                # pcs4 = float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(6))))
                # pcs5 = float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(7))))
                # pcs6 = float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(8))))
                # pcs7 = float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(9))))
                # pcs8 = float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(10))))
                # pcs9 = float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(11))))
                # elemPcs = float((re.sub(r'[^\x00-\x7F]+','-',pcsLn.group(12))))
                # self.pcsL.append([nn[curr], pc, factor, pcs1, pcs2, pcs3, pcs4, pcs5,pcs6,pcs7,pcs8,pcs9,elemPcs])

                if cnt == 4:
                    curr += 1
                    cnt = 0
                else:   
                    cnt += 1

        for i in nn:
            tots.append(i)
        curr = 0


        for ln in self.txt.split("\n"):
            finder = progComp.search(ln)
            if finder: 
                tesBV = (prev.split())[0]
                tesTot = (prev.split())[1]
                tots[curr].append(tesBV)
                tots[curr].append(tesTot)
                curr += 1
            prev = ln

        
        curr =0 
  
        deduc = re.compile(r'(?:Deductions(?-s:.))')
        for ln in self.txt.split("\n"):
            deducLn = deduc.search(ln)
            if deducLn:
                pcsTot = prev[len(prev)-5:]
                ded = ln[len(ln)-5:]
                tots[curr].append(pcsTot)
                tots[curr].append(ded)
                curr += 1
            prev = ln
        curr = 0
        cnt = 0
        for ln in self.txt.split("\n"):
            ln = elementRegex.search(ln)
            if ln:
                
                elemNum = ln.group(1)
                elem = ln.group(1) +". " + ln.group(2)
                base = float(ln.group(3))
                jGoe = float(ln.group(4))
                currLine = [elem, base, jGoe]

                if ln.group(5) == "-":
                    for i in range(self.numJudges):
                        currLine.append(0.0)
                else:
                    for i in range(self.numJudges):
                        currLine.append(float((re.sub(r'[^\x00-\x7F]+','-',ln.group(i+5)))))
                    for i in range(self.numJudges + 1, 10):
                        currLine.append(0.0)
                
                currLine.append(float(ln.group(self.numJudges + 5)))

                #elemTot = "{:.2f}".format(float(ln.group(14)))
                # elemTot = float(ln.group(14))
                lnIt.append(currLine)
                self.allJumps.append(currLine)
                lineWName = currLine.copy().insert(0,[nn[curr][0]])
                # print(currLine)
                if "Sp" in elem:
                    spin.append(lineWName)
                elif "StSq" in elem:
                    stsq.append(lineWName)
                elif "ChSq" in elem:
                    chsq.append(lineWName)
                else:
                    jumps.append(lineWName)             
                cnt += 1
                if cnt == self.numElems:
                   if len(self.info) > 0:
                        
                        h = self.jumpData(lnIt)    
                        pcs = self.pcsData(self.pcsL)
                        totals = self.tot(tots)
                        hL.append([h, totals, pcs])
                        # hL.append(h)
                        cnt = 0
                        curr += 1
                        lnIt = []
                        self.info = self.info[1:]
                        self.pcsL = self.pcsL[5:]
                        tots = tots[1:]


        with open((compName + "/protos.html"),'w') as outFile:
            dphtml = r'<head><meta charset="UTF-8"></head><link rel="stylesheet" type="text/css"  href="../../../style.css">' +'\n'
            dphtml += '<div style="display:flex;justify-content:flex-start;align-items: flex-end;"> '
            dphtml += "<title>"+title+"</title><a href='"+url+"' target='_blank'><h1>"+title+" Protocols</a></h1>"
            dphtml += "<a href='../../../index.html'><h4 style='margin-left:23%;'>Home</a></h1><br><br></div>\n"
            dphtml += '<div class="wrapper"><div class ="main">'
            sidebar = []
            print(len(hL))
            for i in hL:
                dphtml += (i[0].set_table_attributes('class = "tes"').to_html())
                dphtml +=  '</table><br>'                
                dphtml += (i[2].set_table_attributes('class = "pcs"').to_html())
                dphtml +=  '</table><br>'  
                dphtml += (i[1].set_table_attributes('class = "tot"').to_html())
                dphtml += '<br><br><br>'

                info = i[0].to_html()
                id = info[info.find("table id") + 10:info.find("table id") + 17]
                name = info[info.find("caption") + 8:info.find("/caption") - 1]
                sidebar.append([name, id])

            dphtml += '</body>\n</div>\n<div class="sidebar">'
            dphtml += '<div class="jumpto">Jump To</div>'
            for skater in sidebar:
                dphtml += '<div style="margin:7px"><a href="#' + skater[1] + '">' +skater[0]+ '</a></div>\n'

            dphtml += '</div></div>'


            outFile.write(dphtml)


        # jumpbyGOE = elemByGOE(jumps)
        # jmp = rankByScore(jumps, "Highest Scored Jumps By Total Score")
        # stsqs = rankByScore(stsq, "Highest Scored Step Sequences")
        # chsqs = rankByScore(chsq, "Highest Scored Choreo. Sequences")
        # spins = rankByScore(spin, "Highest Scored Spins")
        # bvDf = oneColDf(self.bv, "Base Value", "Highest Base Values")
        # totTesDf = oneColDf(self.totTes, "TES Score", "Highest TES Scores")
        # totPcsDf = oneColDf(self.totPcs, "PCS Score", "Highest PCS Scores")
        # totalS = oneColDf(self.totS, "Total FS Score", "Highest Segment Scores")

        # with open((compName + "/ranks.html"), "w") as outFile:
        #     dphtml = r'<head><meta charset="UTF-8"></head><link rel="stylesheet" type="text/css"  href="../../../../style.css">' +'\n'
        #     dphtml += '<div style="display:flex;justify-content:flex-start;align-items: flex-end;"> '
        #     dphtml += "<title>"+title+"</title><a href='"+url+"' target='_blank'><h1>"+title+" Rankings</a></h1>"
        #     dphtml += "<a href='../../../../index.html'><h4 style='margin-left:5%;'>Home</a></h1><br><br></div>"
        #     dphtml += '<div style="display:flex;justify-content:flex-start;align-items: flex-start;">' + (totalS.set_table_attributes('class = "rk tl" style="float:left;margin-right:70px;" ').to_html()) + '<br><br><br>'
        #     dphtml += (bvDf.set_table_attributes('class = "rk tr" style="margin-right:70px;"').to_html()) + '</div><br><br><br>'
        #     dphtml += '<div style="display:flex;justify-content:flex-start;align-items: flex-start;">' +(totTesDf.set_table_attributes('class = "rk" style="margin-right:70px;"').to_html()) + '<br><br><br>'
        #     dphtml += (totPcsDf.set_table_attributes('class = "rk" style="margin-right:70px;"').to_html()) + '</div><br><br><br>'
        #     dphtml += (jmp.set_table_attributes('class = "rk "').to_html()) + '<br><br><br>'
        #     dphtml += (jumpbyGOE.set_table_attributes('class = "rk"').to_html()) + '<br><br><br>'
        #     dphtml += (stsqs.set_table_attributes('class = "rk"').to_html()) + '<br><br><br>'
        #     dphtml += (chsqs.set_table_attributes('class = "rk"').to_html()) + '<br><br><br>'
        #     dphtml += (spins.set_table_attributes('class = "rk"').to_html()) + '<br><br><br>'

        #     dphtml += '</body>'
        #     outFile.write(dphtml)
                
        
        # print(n)



        #h = df.style.applymap(self.style_negative(props='color:red;'))
        #h.to_html("OLY22FS.html")







            
    # def main(self):
        #self.run("21-22 Beijing Olympics Women\'s Free Skate", "https://results.isu.org/results/season2122/owg2022/FSKWSINGLES-----------FNL-000100--_JudgesDetailsperSkater.pdf", "21-22/olys/w_free")
        #self.run("21-22 Beijing Olympics Mens Free Skate", "https://results.isu.org/results/season2122/owg2022/FSKMSINGLES-----------FNL-000100--_JudgesDetailsperSkater.pdf", "21-22/olys/m_free")

        #self.run("21-22 European Championships Women\'s Free Skate", "http://www.isuresults.com/results/season2122/ec2022/FSKWSINGLES-----------FNL-000100--_JudgesDetailsperSkater.pdf", "21-22/euro/w_free")
        #self.run("21-22 European Championships Mens Free Skate", "http://www.isuresults.com/results/season2122/ec2022/FSKMSINGLES-----------FNL-000100--_JudgesDetailsperSkater.pdf", "21-22/euro/m_free")

        #self.run("20-21 World Championships Women\'s Free Skate", "http://www.isuresults.com/results/season2021/wc2021/FSKWSINGLES-----------FNL-000100--_JudgesDetailsperSkater.pdf", "20-21/wc/w_free")  
        #self.run("20-21 World Championships Mens Free Skate", "http://www.isuresults.com/results/season2021/wc2021/FSKMSINGLES-----------FNL-000100--_JudgesDetailsperSkater.pdf", "20-21/wc/m_free")  
        # 
        # 
        #self.run("21-22 World Championships Womens Free Skate", "https://results.isu.org/results/season2122/wc2022/FSKWSINGLES-----------FNL-000100--_JudgesDetailsperSkater.pdf", "21-22/wc/w_free")       
        #self.run("21-22 World Championships Womens Free Skate", "https://results.isu.org/results/season2122/wc2022/FSKMSINGLES-----------FNL-000100--_JudgesDetailsperSkater.pdf", "21-22/wc/m_free")

        
# bot = OldFreeBot()
# bot.main()
       


