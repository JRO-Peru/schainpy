import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "Meteor Experiment Test"
filename = "meteor20130812.xml"

controllerObj = Project()
controllerObj.setup(id = '191', name='meteor_test01', description=desc)

# path = '/home/dsuarez/.gvfs/datos on 10.10.20.2/High_Power_Meteor'
# 
# path = '/Volumes/FREE_DISK/meteor_data'
# 
# path = '/Users/dsuarez/Movies/meteor'

path = '/home/dsuarez/.gvfs/datos on 10.10.20.2/High_Power_Meteor_Jasmet'

readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2013/08/01',
                                            endDate='2013/08/30',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=1,
                                            delay=5,
                                            walk=0)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileList', 
                     value='1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23,  \
                     25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, \
                     51, 53, 55, 57, 59, 61, 63, 65, 67, 69, 71, 73, 75, \
                     77, 79, 81, 83, 85, 87, 89, 91, 93, 95, 97, 99, 101, \
                     103, 105, 107, 109, 111, 113, 115, 117, 119, 121, 123, \
                     125, 127, 129, 131, 133, 135, 137, 139, 141, 143, 145, \
                     147, 149, 151, 153, 155, 157, 159, 161, 163, 165, 167, \
                     169, 171, 173, 175, 177, 179, 181, 183, 185, 187, 189, \
                     191, 193, 195, 197, 199, 201, 203, 205, 207, 209, 211, \
                     213, 215, 217, 219, 221, 223, 225, 227, 229, 231, 233, \
                     235, 237, 239, 241, 243, 245, 247, 249, 251, 253, 255, \
                     257, 259, 261, 263, 265, 267, 269, 271, 273, 275, 277, \
                     279, 281, 283, 285, 287, 289, 291, 293, 295, 297, 299, \
                     301, 303, 305, 307, 309, 311, 313, 315, 317, 319, 321, \
                     323, 325, 327, 329, 331, 333, 335, 337, 339, 341, 343, \
                     345, 347, 349, 351, 353, 355, 357, 359, 361, 363, 365, \
                     367, 369, 371, 373, 375, 377, 379, 381, 383, 385, 387, \
                     389, 391, 393, 395, 397, 399, 401, 403, 405, 407, 409, \
                     411, 413, 415, 417, 419, 421, 423, 425, 427, 429, 431, \
                     433, 435, 437, 439, 441, 443, 445, 447, 449, 451, 453, \
                     455, 457, 459, 461, 463, 465, 467, 469, 471, 473, 475, \
                     477, 479, 481, 483, 485, 487, 489, 491, 493, 495, 497, \
                     499, 501, 503, 505, 507, 509, 511, 513, 515, 517, 519, \
                     521, 523, 525, 527, 529, 531, 533, 535, 537, 539, 541, \
                     543, 545, 547, 549, 551, 553, 555, 557, 559, 561, 563, \
                     565, 567, 569, 571, 573, 575, 577, 579, 581, 583, 585, \
                     587, 589, 591, 593, 595, 597, 599, 601, 603, 605, 607, \
                     609, 611, 613, 615, 617, 619, 621, 623, 625, 627, 629, \
                     631, 633, 635, 637, 639, 641, 643, 645, 647, 649, 651, \
                     653, 655, 657, 659, 661, 663, 665, 667, 669, 671, 673, \
                     675, 677, 679, 681, 683, 685, 687, 689, 691, 693, 695, \
                     697, 699, 701, 703, 705, 707, 709, 711, 713, 715, 717, \
                     719, 721, 723, 725, 727, 729, 731, 733, 735, 737, 739, \
                     741, 743, 745, 747, 749, 751, 753, 755, 757, 759, 761, \
                     763, 765, 767, 769, 771, 773, 775, 777, 779, 781, 783, \
                     785, 787, 789, 791, 793, 795, 797, 799', format='intlist')

# opObj11 = procUnitConfObj0.addOperation(name='filterByHeights')
# opObj11.addParameter(name='window', value='3', format='int')

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value='1,1,1,1,1,-1,-1,1,1,-1,1,-1,1', format='floatlist')
opObj11.addParameter(name='nCode', value='1', format='int')
opObj11.addParameter(name='nBaud', value='13', format='int')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='400', format='int')

opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='5', format='int')

opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='100', format='int')
opObj11.addParameter(name='wintitle', value='MeteorSpectra', format='str')
opObj11.addParameter(name='zmin', value='10', format='float')
opObj11.addParameter(name='zmax', value='40', format='float')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/meteor_root', format='str')
opObj11.addParameter(name='ftp', value='1', format='int')
opObj11.addParameter(name='wr_period', value='1', format='int')
opObj11.addParameter(name='exp_code', value='15', format='int')

opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='101', format='int')
opObj11.addParameter(name='wintitle', value='MeteorRTI', format='str')
opObj11.addParameter(name='xmin', value='0', format='float')
opObj11.addParameter(name='xmax', value='24', format='float')
opObj11.addParameter(name='zmin', value='10', format='float')
opObj11.addParameter(name='zmax', value='40', format='float')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/meteor_root', format='str')
opObj11.addParameter(name='ftp', value='1', format='int')
opObj11.addParameter(name='wr_period', value='1', format='int')
opObj11.addParameter(name='exp_code', value='15', format='int')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
