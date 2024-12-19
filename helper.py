from get_prof_list import ProfessorList
from get_abstract import ResearchAbstract
from get_researches_of_prof import ProfResearches
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Email_Creater:
    def __init__(self, url, regions):
        self.url = url
        self.regions = regions

    def get_data(self):
        data = self._get_prof_list()
        newText=""
        lines=data.splitlines()
        for line in lines:
            line=line.strip()
            if line.startswith("[Link:"):
                start_index=line.find("http")
                end_index=line.find("]",start_index)
                prof_url=line[start_index:end_index]
                newText= newText + self._get_prof_researches(prof_url)
            else :
                newText+="\n"
                newText+=line
        x=newText.splitlines()
        y=x[:10]
        newText="\n".join(y)

        researches = []
        lines=newText.splitlines()
        logging.info(newText)
        counter=1
        for line in lines:
            newText2=""
            line=line.strip()
            if line.startswith("https://"):
                research_url=line
                newText2+="\n"
                newText2+=f"Abstract for Research Paper {counter}"
                newText2+="\n"
                newText2+="\n"
                newText2+=self._get_research_abstract(research_url)
                newText2+="\n"
                counter+=1
                logging.info(newText2)
            else :
                counter=1
                newText2+=line
                newText2+="\n"
            logging.info(newText2)
            researches.append(newText2)

        return researches

    def _get_prof_list(self):
        prof_list = ProfessorList(self.url, self.regions)
        return prof_list.getProfList()
    
    def _get_prof_researches(self, prof_url):
        prof_researches = ProfResearches(prof_url)
        return prof_researches.getProfResearches()
    
    def _get_research_abstract(self, research_url):
        research_abstract = ResearchAbstract(research_url)
        return research_abstract.getResearchAbstract()