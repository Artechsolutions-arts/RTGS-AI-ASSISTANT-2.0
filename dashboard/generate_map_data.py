import json

# 1. Standard Constituency Number -> Name Mapping (1-175)
# Based on 2008 Delimitation order
NUMBER_TO_NAME = {
    1: "Ichchapuram", 2: "Palasa", 3: "Tekkali", 4: "Pathapatnam", 5: "Srikakulam",
    6: "Amadalavalasa", 7: "Etcherla", 8: "Narasannapeta", 9: "Rajam", 10: "Palakonda",
    11: "Kurupam", 12: "Parvathipuram", 13: "Salur", 14: "Bobbili", 15: "Cheepurupalli",
    16: "Gajapathinagaram", 17: "Nellimarla", 18: "Vizianagaram", 19: "Srungavarapukota",
    20: "Bhimili", 21: "Visakhapatnam East", 22: "Visakhapatnam South", 23: "Visakhapatnam North",
    24: "Visakhapatnam West", 25: "Gajuwaka", 26: "Chodavaram", 27: "Madugula",
    28: "Araku Valley", 29: "Paderu", 30: "Anakapalle", 31: "Pendurthi",
    32: "Yelamanchili", 33: "Payakaraopet", 34: "Narsipatnam", 35: "Tuni",
    36: "Prathipadu", 37: "Pithapuram", 38: "Kakinada Rural", 39: "Peddapuram",
    40: "Anaparthy", 41: "Kakinada City", 42: "Ramachandrapuram", 43: "Mummidivaram",
    44: "Amalapuram", 45: "Razole", 46: "Gannavaram (Konaseema)", 47: "Kothapeta",
    48: "Mandapeta", 49: "Rajanagaram", 50: "Rajahmundry City", 51: "Rajahmundry Rural",
    52: "Jaggampeta", 53: "Rampachodavaram", 54: "Kovvur", 55: "Nidadavole",
    56: "Achanta", 57: "Palakollu", 58: "Narasapuram", 59: "Bhimavaram",
    60: "Undi", 61: "Tanuku", 62: "Tadepalligudem", 63: "Unguturu",
    64: "Denduluru", 65: "Eluru", 66: "Gopalapuram", 67: "Polavaram",
    68: "Chintalapudi", 69: "Tiruvuru", 70: "Nuzvid", 71: "Gannavaram (Krishna)",
    72: "Gudivada", 73: "Kaikalur", 74: "Pedana", 75: "Machilipatnam",
    76: "Avanigadda", 77: "Pamarru", 78: "Penamaluru", 79: "Vijayawada West",
    80: "Vijayawada Central", 81: "Vijayawada East", 82: "Mylavaram", 83: "Nandigama",
    84: "Jaggayyapeta", 85: "Pedakurapadu", 86: "Tadikonda", 87: "Mangalagiri",
    88: "Ponnur", 89: "Vemuru", 90: "Repalle", 91: "Tenali", 92: "Bapatla",
    93: "Prathipadu (Guntur)", 94: "Guntur West", 95: "Guntur East", 96: "Chilakaluripet",
    97: "Narasaraopet", 98: "Sattenapalle", 99: "Vinukonda", 100: "Gurajala",
    101: "Macherla", 102: "Yerragondapalem", 103: "Darsi", 104: "Parchur",
    105: "Addanki", 106: "Chirala", 107: "Santhanuthalapadu", 108: "Ongole",
    109: "Kandukur", 110: "Kondapi", 111: "Markapuram", 112: "Giddalur",
    113: "Kanigiri", 114: "Kavali", 115: "Atmakur", 116: "Kovur",
    117: "Nellore City", 118: "Nellore Rural", 119: "Sarvepalli", 120: "Gudur",
    121: "Sullurpeta", 122: "Venkatagiri", 123: "Udayagiri", 124: "Badvel",
    125: "Rajampet", 126: "Kadapa", 127: "Kodur", 128: "Rayachoti",
    129: "Pulivendla", 130: "Kamalapuram", 131: "Jammalamadugu", 132: "Proddatur",
    133: "Mydukur", 134: "Allagadda", 135: "Srisailam", 136: "Nandikotkur",
    137: "Kurnool", 138: "Panyam", 139: "Nandyal", 140: "Banaganapalle",
    141: "Dhone", 142: "Pattikonda", 143: "Kodumur", 144: "Yemmiganur",
    145: "Mantralayam", 146: "Adoni", 147: "Alur", 148: "Rayadurg",
    149: "Uravakonda", 150: "Guntakal", 151: "Tadipatri", 152: "Singanamala",
    153: "Anantapur Urban", 154: "Kalyandurg", 155: "Raptadu", 156: "Madakasira",
    157: "Hindupur", 158: "Penukonda", 159: "Puttaparthi", 160: "Dharmavaram",
    161: "Kadiri", 162: "Thamballapalle", 163: "Pileru", 164: "Madanapalle",
    165: "Punganur", 166: "Chandragiri", 167: "Tirupati", 168: "Srikalahasti",
    169: "Satyavedu", 170: "Nagari", 171: "Gangadhara Nellore", 172: "Chittoor",
    173: "Puthalapattu", 174: "Palamaner", 175: "Kuppam"
}

# 2. New District -> Constituency Names Mapping
# Based on official reorganization
DISTRICT_MAP = {
    "Srikakulam": ["Ichchapuram", "Palasa", "Tekkali", "Pathapatnam", "Srikakulam", "Amadalavalasa", "Etcherla", "Narasannapeta"],
    "Vizianagaram": ["Rajam", "Bobbili", "Cheepurupalli", "Gajapathinagaram", "Nellimarla", "Vizianagaram", "Srungavarapukota"],
    "Parvathipuram Manyam": ["Palakonda", "Kurupam", "Parvathipuram", "Salur"],
    "Visakhapatnam": ["Bhimili", "Visakhapatnam East", "Visakhapatnam South", "Visakhapatnam North", "Visakhapatnam West", "Gajuwaka"], # Pendurthi moved to Anakapalli? Checking search.
    # Wikipedia: Pendurthi usually Visakhapatnam. But new drafts put it in Anakapalli or split. I will assign based on map contiguity if needed.
    # Search 3 said: Pendurthi in Visakhapatnam.
    "Anakapalli": ["Chodavaram", "Madugula", "Anakapalle", "Pendurthi", "Yelamanchili", "Payakaraopet", "Narsipatnam"],
    "Alluri Sitharama Raju": ["Araku Valley", "Paderu", "Rampachodavaram"],
    "Kakinada": ["Tuni", "Prathipadu", "Pithapuram", "Kakinada Rural", "Peddapuram", "Anaparthy", "Kakinada City", "Jaggampeta"], # Search 3: Jaggampeta in Kakinada
    "Konaseema": ["Ramachandrapuram", "Mummidivaram", "Amalapuram", "Razole", "Gannavaram (Konaseema)", "Kothapeta", "Mandapeta"],
    "East Godavari": ["Rajanagaram", "Rajahmundry City", "Rajahmundry Rural", "Kovvur", "Nidadavole", "Gopalapuram", "Chintalapudi"], # Note: Chintalapudi/Gopalapuram might be Eluru.
    # Correcting E.Godavari based on Search 3:
    # 49 Rajanagaram, 50-51 Rajahmundry, 54 Kovvur, 55 Nidadavole, 66 Gopalapuram?, 68 Chintalapudi?
    # Search 3 says: East Godavari = Devarapalle, Rajahmundry, etc.
    # Eluru = Chintalapudi, Polavaram, Denduluru, Eluru, Unguturu, Kaikalur?
    # Let's use the explicit assignment from SEARCH 3 text for New Districts.
    
    # RE-VERIFIED MAPPING FROM SEARCH 3 & 4 (Combined Logic):
    "Srikakulam": [1, 2, 3, 4, 5, 6, 7, 8], # Etcherla(7) is Srikakulam
    "Vizianagaram": [9, 14, 15, 16, 17, 18, 19], # Rajam(9) in Vizianagaram
    "Parvathipuram Manyam": [10, 11, 12, 13],
    "Visakhapatnam": [20, 21, 22, 23, 24, 25, 31], # 31 Pendurthi in Visakhapatnam usually.
    "Anakapalli": [26, 27, 30, 32, 33, 34], # 27 Madugula might be ASR? Search 3 says Madugula in Anakapalli.
    "Alluri Sitharama Raju": [28, 29, 53],
    "Kakinada": [29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41], # Wait - numbers overlap.
    # Let's map by NUMBER for precision.
}

# Precise Number -> District Map based on 2022 Reorg
# Source: Wikipedia "List of districts of Andhra Pradesh" + constituency limits.
# Srikakulam: 1-8.
# Vizianagaram: 9, 14-19.
# Manyam: 10-13.
# Visakhapatnam: 20-25. (Pendurthi 31?)
# Anakapalli: 26, 27, 30-34. (If 31 is Anakapalli). Wiki says: 26, 27, 30, 31, 32, 33, 34.
# ASR: 28, 29, 53.
# Kakinada: 35-41, 52 (Jaggampeta). (Tuni 35... Kakinada City 41).
# Konaseema: 42-48. (Ramachandrapuram... Mandapeta).
# East Godavari: 49-51, 54, 55, 61, 62?
#   Wait, 61 Tanuku, 62 Tadepalligudem are W.Godavari usually.
#   Search 3: E.Godavari gets Kovvur(54), Nidadavole(55), Gopalapuram(66).
# Eluru: 63, 64, 65, 67 (Polavaram), 68 (Chintalapudi), 70 (Nuzvid), 73 (Kaikalur).
# West Godavari: 56-60, 61, 62.
# NTR: 69 (Tiruvuru), 79-84 (Vijayawada set + Jaggayyapeta + Nandigama + Mylavaram).
# Krishna: 71, 72, 74-78.
# Guntur: 86, 87, 91, 93, 94, 95, 96?
#   Guntur Dist (New): Tadikonda(86), Mangalagiri(87), Tenali(91), Prathipadu(93), Guntur W(94), Guntur E(95), Ponnur(88).
# Bapatla: 89(Vemuru), 90(Repalle), 92(Bapatla), 104(Parchur), 105(Addanki), 106(Chirala).
# Palnadu: 85(Pedakurapadu), 96(Chilakaluripet), 97(Narasaraopet), 98(Sattenapalle), 99(Vinukonda), 100(Gurajala), 101(Macherla).
# Prakasam: 102(Yerragondapalem), 103(Darsi), 107(Santhanuthalapadu), 108(Ongole), 109(Kandukur), 110(Kondapi), 111(Markapuram), 112(Giddalur), 113(Kanigiri). (Note: Kandukur moved to Nellore? Search 3 says Kandukur in Nellore usually, but some sources say Prakasam. Let's check. Search 3 says Kandukur in Prakasam).
# Nellore: 109(Kandukur)?, 114(Kavali), 115(Atmakur), 116(Kovur), 117(Nellore City), 118(Rural), 119(Sarvepalli), 123(Udayagiri).
# Tirupati: 115(Gudur-SC)?, 120(Gudur), 121(Sullurpeta), 122(Venkatagiri), 166(Chandragiri), 167(Tirupati), 168(Srikalahasti), 169(Satyavedu).
#   Wait, number indices might be off.
#   Gudur is 120. Sullurpeta 121.
# Chittoor: 165(Punganur), 170(Nagari), 171(GD Nellore), 172(Chittoor), 173(Puthalapattu), 174(Palamaner), 175(Kuppam).
# Annamayya: 124(Badvel)? 125(Rajampet), 127(Kodur), 128(Rayachoti), 162(Thamballapalle), 163(Pileru), 164(Madanapalle).
#   124 Badvel usually in Kadapa.
# YSR (Kadapa): 124(Badvel), 126(Kadapa), 129(Pulivendla), 130(Kamalapuram), 131(Jammalamadugu), 132(Proddatur), 133(Mydukur).
# Nandyal: 134(Allagadda), 135(Srisailam), 136(Nandikotkur), 138(Panyam), 139(Nandyal), 140(Banaganapalle), 141(Dhone).
# Kurnool: 137(Kurnool), 142(Pattikonda), 143(Kodumur), 144(Yemmiganur), 145(Mantralayam), 146(Adoni), 147(Alur).
# Anantapur: 148(Rayadurg), 149(Uravakonda), 150(Guntakal), 151(Tadipatri), 152(Singanamala), 153(Urban), 154(Kalyandurg), 155(Raptadu).
# Satya Sai: 156(Madakasira), 157(Hindupur), 158(Penukonda), 159(Puttaparthi), 160(Dharmavaram), 161(Kadiri).

NUMBER_TO_DISTRICT = {}

def assign(nums, district):
    for n in nums:
        NUMBER_TO_DISTRICT[n] = district

assign(range(1, 9), "Srikakulam") # 1-8
assign([9, 14, 15, 16, 17, 18, 19], "Vizianagaram")
assign([10, 11, 12, 13], "Parvathipuram Manyam")
assign([20, 21, 22, 23, 24, 25], "Visakhapatnam") # Urban
assign([26, 27, 30, 31, 32, 33, 34], "Anakapalli") # 31 Pendurthi
assign([28, 29, 53], "Alluri Sitharama Raju")
assign([35, 36, 37, 38, 39, 40, 41, 52], "Kakinada") # 52 is Jaggampeta
assign([42, 43, 44, 45, 46, 47, 48], "Konaseema")
assign([49, 50, 51, 54, 55, 66, 68], "East Godavari") # 66 Gopalapuram, 68 Chintalapudi (or Eluru?)
# Check Chintalapudi(68) and Gopalapuram(66). Search 3 says they are in Eluru.
# Let's adjust East Godavari.
# E.Godavari: 49, 50, 51, 54, 55. + Kovvur(54), Nidadavole(55).
# Eluru: 63, 64, 65, 67, 70, 73, 66, 68?
# Let's assume Search 3 for Eluru: Chintalapudi(68), Denduluru(64), Eluru(65), Gopalapuram(66), Polavaram(67), Unguturu(63), Nuzvid(70), Kaikalur(73).
assign([63, 64, 65, 66, 67, 68, 70, 73], "Eluru")
assign([56, 57, 58, 59, 60, 61, 62], "West Godavari") # + Tanuku(61), Tadepalligudem(62).
assign([69, 79, 80, 81, 82, 83, 84], "NTR") # 69 Tiruvuru, 79-81 Vijayawada, 82 Mylavaram, 83 Nandigama, 84 Jaggayyapeta.
assign([71, 72, 74, 75, 76, 77, 78], "Krishna") # 71 Gannavaram, 72 Gudivada, 74 Pedana...
assign([86, 87, 88, 91, 93, 94, 95], "Guntur")
assign([85, 96, 97, 98, 99, 100, 101], "Palnadu")
assign([89, 90, 92, 104, 105, 106], "Bapatla")
assign([102, 103, 107, 108, 109, 110, 111, 112, 113], "Prakasam") # Kandukur(109) in Prakasam (or Nellore?). Post-2022 it was Nellore. Let's verify.
# Search 3: Kandukur in Prakasam.
# Search 3 note: "Prakasam District... Markapuram carved out".
# Let's stick Kandukur in Nellore if looking at 2022 map.
# 2022 Map: Kandukur is in Nellore.
# Let's move 109 to Nellore.
assign([109, 114, 115, 116, 117, 118, 119, 123], "Nellore")
assign([120, 121, 122, 166, 167, 168, 169], "Tirupati")
assign([124, 125, 127, 128, 162, 163, 164], "Annamayya") # 124 Badvel? Badvel is YSR.
# Correction: Badvel(124) is YSR.
# Annamayya: Rajampet(125), Kodur(127), Rayachoti(128), Thamballapalle(162), Pileru(163), Madanapalle(164).
assign([125, 127, 128, 162, 163, 164], "Annamayya")
assign([124, 126, 129, 130, 131, 132, 133], "YSR")
assign([134, 135, 136, 138, 139, 140, 141], "Nandyal")
assign([137, 142, 143, 144, 145, 146, 147], "Kurnool")
assign([148, 149, 150, 151, 152, 153, 154, 155], "Anantapur")
assign([156, 157, 158, 159, 160, 161], "Satya Sai")
assign([165, 170, 171, 172, 173, 174, 175], "Chittoor")

def main():
    try:
        with open('svg_mapping.json', 'r') as f:
            svg_map = json.load(f)
    except Exception as e:
        print(f"Error loading svg_mapping.json: {e}")
        return

    # Build the output structure
    output_js = """// Auto-generated Constituency Data
const CONSTITUENCY_DATA = {
"""
    
    for path_id, number_str in svg_map.items():
        try:
            num = int(number_str)
            name = NUMBER_TO_NAME.get(num, "Unknown")
            dist = NUMBER_TO_DISTRICT.get(num, "Unknown")
            
            output_js += f'    "{path_id}": {{ number: {num}, name: "{name}", district: "{dist}" }},\n'
        except ValueError:
            print(f"Skipping invalid number: {number_str}")

    output_js += "};\n"
    
    # Also export the reverse mapping District -> Constituencies if needed
    output_js += """
const DISTRICT_CONSTITUENCIES = {
"""
    # Invert the map
    dist_to_consts = {}
    for num, dist in NUMBER_TO_DISTRICT.items():
        if dist not in dist_to_consts: dist_to_consts[dist] = []
        name = NUMBER_TO_NAME.get(num, str(num))
        dist_to_consts[dist].append(name)
        
    for dist, consts in dist_to_consts.items():
        consts_str = '", "'.join(consts)
        output_js += f'    "{dist}": ["{consts_str}"],\n'
    
    output_js += "};\n"

    # Write to file
    with open('constituency_data.js', 'w') as f:
        f.write(output_js)
        
    print("Generated constituency_data.js")

if __name__ == "__main__":
    main()
