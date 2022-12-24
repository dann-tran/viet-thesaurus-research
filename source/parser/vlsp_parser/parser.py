import xml.etree.ElementTree as ET

from typing import List, Optional

from source.parser.vlsp_parser.model import VlspEntry


class VlspParser:
    def parse(self, file: str):
        """
        Outputs a list of (headword, POS, definition, synonyms, antonyms)
        """
        root = ET.parse(file).getroot()

        entries: List[VlspEntry] = []

        for entry in root:
            headword: Optional[str] = None
            pos: Optional[str] = None
            definition: Optional[str] = None
            synonyms: Optional[str] = None
            antonyms: Optional[str] = None

            for child in entry:
                if child.tag == "HeadWord":
                    headword = child.text
                elif child.tag == "Syntactic":
                    cat = child.find("Category")
                    if cat is None:
                        raise Exception("Missing Category tag for POS.")
                    pos = cat.text
                elif child.tag == "Semantic":
                    definition, synonyms, antonyms = self._parseSemanticElem(child)

                if headword is not None and pos is not None and definition is not None:
                    break

            if headword is None:
                raise Exception("Missing headword.")
            if pos is None:
                raise Exception("Missing POS.")
            if definition is None:
                raise Exception("Missing definition.")

            entries.append(VlspEntry(headword, pos, definition, synonyms, antonyms))

        return entries

    def _parseSemanticElem(self, elem: ET.Element):
        definition: Optional[str] = None
        synonyms: Optional[str] = None
        antonyms: Optional[str] = None

        for child in elem:
            if child.tag == "def":
                definition = self._getElemText(child)
            elif child.tag == "LogicalConstraint":
                synonyms, antonyms = self._parseSemanticLogicalConstraint(child)

        return definition, synonyms, antonyms

    def _parseSemanticLogicalConstraint(self, elem: ET.Element):
        synonyms: Optional[str] = None
        antonyms: Optional[str] = None

        for child in elem:
            if child.tag == "Synonym":
                synonyms = child.text
            elif child.tag == "Antonym":
                antonyms = child.text

        return synonyms, antonyms

    def _getElemText(self, elem: ET.Element):
        tag = elem.tag
        raw_text = ET.tostring(elem, encoding="unicode")
        open_tag, close_tag = f"<{tag}>", f"</{tag}>"

        start_idx = len(open_tag)
        if not raw_text.startswith(open_tag):
            raise Exception(f"Expects {tag} but actual is {raw_text[:start_idx]}")
        end_idx = raw_text.find(close_tag, start_idx)

        return raw_text[start_idx:end_idx].strip()
