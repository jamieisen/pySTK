import comtypes
from comtypes.client import CreateObject
comtypes.client.GetModule((comtypes.GUID("{FEAEF02E-48CE-42AE-B99B-FB9871A69E4B}") ,1,0))
from comtypes.gen import AgStkGatorLib

class pySTK:

	# Initializes STK, Opens Application, Defines Root, Track Number of Windows
	def __init__(self):
		self.stk = CreateObject('STK12.Application')
		self.stk.Visible=True
		self.stk.UserControl=True
		self.root=self.stk.Personality2
		self.numberOfWindows = 2

	# Define scenario, its name, start epoch, end epoch
	def Scenario(self,name,start,end):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		self.root.NewScenario(name)
		self.scenarioName = name
		self.scenario = self.root.CurrentScenario
		self.scenarioInterface = self.scenario.QueryInterface(STKObjects.IAgScenario)
		self.scenarioInterface.SetTimePeriod(start,end)
		self.root.Rewind()
		return self.scenarioInterface

	# Load a scenario from a filepath
	def LoadScenario(self,filePath):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		self.root.LoadScenario(str(filePath))
		self.scenario = self.root.CurrentScenario
		self.scenarioInterface = self.scenario.QueryInterface(STKObjects.IAgScenario)
		return self.scenarioInterface

	def Sensor(self,parent,name):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		parent = self.scenario.Children(str(parent))
		sensor = parent.Children.New(STKObjects.eSensor,str(name))
		sensorInterface = sensor.QueryInterface(STKObjects.IAgSensor)
		return sensorInterface

	def SARSensor(self,parent,name,minElev,maxElev,foreExclusionAngle,aftExclusionAngle,parentAltitude):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		parent = self.scenario.Children(str(parent))
		sensor = parent.Children.New(STKObjects.eSensor,str(name))
		sensorInterface = sensor.QueryInterface(STKObjects.IAgSensor)
		sensorInterface.SetPatternType(STKObjects.eSnSAR)
		sensorInterface.CommonTasks.SetPatternSAR(minElev,maxElev,foreExclusionAngle,aftExclusionAngle,parentAltitude)
		return sensorInterface

	def Place(self,name,centralBody,lat,longi):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		self.scenario.CentralBodyName
		place = self.scenario.Children.NewOnCentralBody(STKObjects.ePlace,str(name),str(centralBody))
		placeInterface = place.QueryInterface(STKObjects.IAgPlace)
		placeInterface.Position.AssignGeodetic(lat,longi,0)
		placeInterface.UseTerrain = True
		return placeInterface

	def Facility(self,name,lat,longi,elev):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		facility = self.scenario.Children.New(STKObjects.eFacility,name)
		facilityInterface = facility.QueryInterface(STKObjects.IAgFacility)
		facilityInterface.Position.AssignGeodetic(lat,longi,elev)
		return facilityInterface

	def Antenna(self,parent,name):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		parent = self.scenario.Children(parent)
		antenna = parent.Children.New(STKObjects.eAntenna,name)
		antennaInterface = antenna.QueryInterface(STKObjects.IAgAntenna)
		return antennaInterface

	def DipoleAntenna(self,parent,name,freq,eff,length):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		antenna = self.Antenna(parent,name)
		antenna.SetModel('Dipole')
		antenna.Model.DesignFrequency = freq
		dipole = antenna.Model.QueryInterface(STKObjects.IAgAntennaModelDipole)
		dipole.Efficiency = eff
		dipole.Length = length
		return dipole

	def ParabolicAntenna(self,parent,name,freq,diam,eff):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		parent = self.scenario.Children(parent)
		antenna = parent.Children.New(STKObjects.eAntenna,name)
		antennaInterface = antenna.QueryInterface(STKObjects.IAgAntenna)
		antennaInterface.SetModel('Parabolic')
		antennaInterface.Model.DesignFrequency = freq
		antennaModel = antennaInterface.Model.QueryInterface(STKObjects.IAgAntennaModelParabolic)
		antennaModel.Diameter = diam 
		antennaModel.Efficiency = eff
		return antennaInterface
	
	def ComplexTx(self,name,parent,freq,pwr,dataR,ant):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		parent = self.scenario.Children(parent)
		Tx = parent.Children.New(STKObjects.eTransmitter,name)
		TxInterface = Tx.QueryInterface(STKObjects.IAgTransmitter)
		TxInterface.SetModel('Complex Transmitter Model')
		TxComplexModel = TxInterface.Model.QueryInterface(STKObjects.IAgTransmitterModelComplex)
		TxComplexModel.Frequency = freq
		TxComplexModel.Power = pwr
		TxComplexModel.DataRate = dataR
		TxAntennaControl = TxComplexModel.AntennaControl
		TxAntennaControl.ReferenceType = 0 #'eAntennaControlRefTypeLink'
		TxAntennaControl.LinkedAntennaObject = 'Antenna/'+str(ant)
		return TxInterface

	def ComplexRx(self,name,parent,LNAg,ant):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		parent = self.scenario.Children(parent)
		Rx = parent.Children.New(STKObjects.eReceiver,name)
		RxInterface = Rx.QueryInterface(STKObjects.IAgReceiver)
		RxInterface.SetModel('Complex Receiver Model')
		RxComplexModel = RxInterface.Model.QueryInterface(STKObjects.IAgReceiverModelComplex)
		RxComplexModel.LnaGain = LNAg
		RxAntennaControl = RxComplexModel.AntennaControl
		RxAntennaControl.ReferenceType = 0 #'eAntennaControlRefTypeLink'
		RxAntennaControl.LinkedAntennaObject = 'Antenna/'+str(ant)
		return RxInterface

	def Planet(self,name):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		planet = self.scenario.Children.New(STKObjects.ePlanet,name)
		planInterface = planet.QueryInterface(STKObjects.IAgPlanet)
		planInterface.CommonTasks.SetPositionSourceCentralBody(name,STKObjects.eEphemJPLDE)
		self.root.ExecuteCommand('ComponentBrowser */ Duplicate "Propagators" "Earth Point Mass" '+str(name)+'PointMass')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Propagators" '+str(name)+'PointMass CentralBody '+str(name))
		return planInterface

	def Asteroid(self,asteroidName,fileName,radius,gravityAcceleration):#mu):
		# Requires results files from NASA HORIZONS 
		# and plug in for HORIZONS 
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		asteroid = self.scenario.Children.New(STKObjects.eSatellite,str(asteroidName))
		astInterface = asteroid.QueryInterface(STKObjects.IAgSatellite)
		astInterface.SetPropagatorType(STKObjects.ePropagatorStkExternal)
		astProp = astInterface.Propagator.QueryInterface(STKObjects.IAgVePropagatorStkExternal)
		astProp.Filename = fileName
		astProp.Override = True
		astProp.Propagate()
		astInterface.ExportTools.GetEphemerisStkExportTool().Export(str(asteroidName)+'.e')
		asteroidComponent = self.scenarioInterface.ComponentDirectory.GetComponents(2).GetFolder('Central Bodies').DuplicateComponent(1,str(asteroidName))
		ePhemInterface = asteroidComponent.QueryInterface(AgStkGatorLib.IAgVACentralBody).AddEphemeris(1,str(asteroidName)+'.e')
		ePhemInterface.QueryInterface(AgStkGatorLib.IAgVACbEphemerisFile).Filename = str(asteroidName)+'.e'
		asteroidComponent.QueryInterface(AgStkGatorLib.IAgVACentralBody).SetDefaultEphemerisByName(str(asteroidName)+'_e')
		asteroidComponent.QueryInterface(AgStkGatorLib.IAgVACentralBody).DefaultShapeData.QueryInterface(AgStkGatorLib.IAgVACbShapeSphere).Radius = radius
		#try setting shape 
		asteroidComponent.QueryInterface(AgStkGatorLib.IAgVACentralBody).DefaultGravityModelData.QueryInterface(AgStkGatorLib.IAgVACbGravityModel).RefDistance = radius
		asteroidComponent.QueryInterface(AgStkGatorLib.IAgVACentralBody).GravitationalParam = gravityAcceleration
		#asteroidComponent.QueryInterface(AgStkGatorLib.IAgVACentralBody).DefaultGravityModelData.QueryInterface(AgStkGatorLib.IAgVACbGravityModel).GravitationalParam = mu
		self.scenario.Children.Unload(STKObjects.eSatellite,str(asteroidName))
		planet = self.scenario.Children.New(STKObjects.ePlanet,asteroidName)
		planInterface = planet.QueryInterface(STKObjects.IAgPlanet)
		planInterface.CommonTasks.SetPositionSourceCentralBody(str(asteroidName),STKObjects.eEphemDefault)
		self.root.ExecuteCommand('ComponentBrowser */ Duplicate "Propagators" "Earth Point Mass" '+str(asteroidName)+'PointMass')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Propagators" '+str(asteroidName)+'PointMass CentralBody '+str(asteroidName))
		return astInterface

	def J2Sat(self,name,centralBody,epoch,n,e,i,w,RAAN,theta):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		#satellite = self.scenario.Children.New(STKObjects.eSatellite,name)
		satellite = self.scenario.Children.NewOnCentralBody(STKObjects.eSatellite,str(name),str(centralBody))
		satInterface = satellite.QueryInterface(STKObjects.IAgSatellite)
		satInterface.SetPropagatorType(STKObjects.ePropagatorJ2Perturbation)
		satProp = satInterface.Propagator.QueryInterface(STKObjects.IAgVePropagatorJ2Perturbation)
		satProp.InitialState.Epoch=epoch
		keplerian = satProp.InitialState.Representation.ConvertTo(STKUtil.eOrbitStateClassical)
		kepInterface = keplerian.QueryInterface(STKObjects.IAgOrbitStateClassical)
		kepInterface.SizeShapeType = STKObjects.eSizeShapeMeanMotion
		kepInterface.LocationType = STKObjects.eLocationMeanAnomaly
		kepInterface.Orientation.AscNodeType = STKObjects.eAscNodeRAAN
		self.root.UnitPreferences.Item('AngleUnit').SetCurrentUnit('revs')
		self.root.UnitPreferences.Item('TimeUnit').SetCurrentUnit('day')
		kepInterface.SizeShape.QueryInterface(STKObjects.IAgClassicalSizeShapeMeanMotion).MeanMotion = n
		kepInterface.SizeShape.QueryInterface(STKObjects.IAgClassicalSizeShapeMeanMotion).Eccentricity = e
		self.root.UnitPreferences.Item('AngleUnit').SetCurrentUnit('deg')
		self.root.UnitPreferences.Item('TimeUnit').SetCurrentUnit('sec')
		kepInterface.Orientation.Inclination = i
		kepInterface.Orientation.ArgOfPerigee = w
		kepInterface.Orientation.AscNode.QueryInterface(STKObjects.IAgOrientationAscNodeRAAN).value = RAAN
		kepInterface.Location.QueryInterface(STKObjects.IAgClassicalLocationMeanAnomaly).Value = theta
		satProp.InitialState.Representation.Assign(keplerian)
		satProp.Propagate()
		return satInterface

	def TwoBodySat(self,name,centralBody,epoch):
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		satellite = self.scenario.Children.NewOnCentralBody(STKObjects.eSatellite,str(name),str(centralBody))
		satInterface = satellite.QueryInterface(STKObjects.IAgSatellite)
		satInterface.SetPropagatorType(STKObjects.ePropagatorTwoBody)
		satProp = satInterface.Propagator.QueryInterface(STKObjects.IAgVePropagatorTwoBody)
		satProp.InitialState.Epoch = epoch
		return satInterface

	# Sets STK scenario for interplanetary work
	def InterplaneteryMode(self):
		self.root.ExecuteCommand('SetUnits / km')
		self.root.ExecuteCommand('SetInterplanetaryMode / On')
		self.root.ExecuteCommand('Graphics */Scenario/'+str(self.scenarioName)+' GlobalAttributes ShowPlanetOrbits On')
		self.root.ExecuteCommand('Graphics */Scenario/'+str(self.scenarioName)+' GlobalAttributes ShowPlanetGroundLabel Off')
		self.root.ExecuteCommand('Graphics */Scenario/'+str(self.scenarioName)+' GlobalAttributes ShowPlanetGroundPos Off')
		self.root.ExecuteCommand('Window2D * Remove WindowID 1')
		self.root.ExecuteCommand('VO * CentralBody Sun 1')  
		self.root.ExecuteCommand('VO * Grids Space ShowECI On ECIColor %105105105 WindowID 1')
		self.root.ExecuteCommand('VO * View Top Zoom WindowID 1')
		self.root.ExecuteCommand('Window3D * ViewVolume MaxVisibleDist 1e12 WindowID 1')
		self.root.ExecuteCommand('VO * ViewerPosition 30 190 1000000000 1')
		self.numberOfWindows = self.numberOfWindows - 1

	# Adds a 3D Viewer of a central body (up to 6 windows)
	def planetView(self,planetName):
		self.numberOfWindows = self.numberOfWindows + 1
		self.root.ExecuteCommand('Window3D * CreateWindow Type Normal')
		self.root.ExecuteCommand('VO * CentralBody '+str(planetName)+' '+str(self.numberOfWindows))
		if self.numberOfWindows == 2:
			self.root.ExecuteCommand('Window3D * Place 555 0 WindowID '+str(self.numberOfWindows))
			self.root.ExecuteCommand('Window3D * Size 555 460 WindowID '+str(self.numberOfWindows))
		if self.numberOfWindows == 3:
			self.root.ExecuteCommand('Window3D * Place 1110 0 WindowID '+str(self.numberOfWindows))
			self.root.ExecuteCommand('Window3D * Size 555 460 WindowID '+str(self.numberOfWindows))
		if self.numberOfWindows == 4:
			self.root.ExecuteCommand('Window3D * Place 0 450 WindowID '+str(self.numberOfWindows))
			self.root.ExecuteCommand('Window3D * Size 555 300 WindowID '+str(self.numberOfWindows))
		if self.numberOfWindows == 5:
			self.root.ExecuteCommand('Window3D * Place 555 450 WindowID '+str(self.numberOfWindows))
			self.root.ExecuteCommand('Window3D * Size 555 300 WindowID '+str(self.numberOfWindows))
		if self.numberOfWindows == 6:
			self.root.ExecuteCommand('Window3D * Place 1110 450 WindowID '+str(self.numberOfWindows))
			self.root.ExecuteCommand('Window3D * Size 555 300 WindowID '+str(self.numberOfWindows))

	# Uses the design tool Lambert Solver to solve the trajectory between two central bodies
	## NOTE TO SELF - try to code without Execute Command and move to AstroSat
	def InterplanetaryLambertSolver(self,name,centralbody,initEpoch,minimumTOF,depBody,arrBody,propagator,arrRadius,depRadius,depCirc,arrCirc):
		self.root.ExecuteCommand('ComponentBrowser */ Duplicate "Design Tools" "Lambert Solver"'+str(name))
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' LambertToolMode "Specify initial and final central bodies"')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' CentralBody "'+str(centralbody)+'"')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' InitEpoch "'+str(initEpoch)+' UTCG"')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' MinimumTOF "'+str(minimumTOF)+'"')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' Departure.CentralBody "'+str(depBody)+'"')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' Arrival.CentralBody "'+str(arrBody)+'"')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' Propagator "'+str(propagator)+'"')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' SequenceName "'+str(name)+'"')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' Departure.UseCircVel '+str(depCirc))
		if depCirc == 'true':
			self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' Departure.ConsiderGravity true')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' Arrival.UseCircVel '+str(arrCirc))
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' Arrival.RadiusScaleFactor "'+str(arrRadius)+'"')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Design Tools"'+str(name)+' Departure.RadiusScaleFactor "'+str(depRadius)+'"')
		self.root.ExecuteCommand('ComponentBrowser */ LambertCompute "Design Tools" '+str(name))
		self.root.ExecuteCommand('ComponentBrowser */ LambertConstructSequence "Design Tools" '+str(name))
		self.root.ExecuteCommand('ComponentBrowser */ LambertAddToCB "Design Tools" '+str(name))

	## NOTE TO SELF - try to code without Execute Command and move to AstroSat
	def IspThrustEngine(self,name,thrust,isp):
		self.root.ExecuteCommand('ComponentBrowser */ Duplicate "Engine Models" "Constant Thrust and Isp" '+str(name))
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Engine Models"'+str(name)+' Thrust "'+str(thrust)+'"')
		self.root.ExecuteCommand('ComponentBrowser */ SetValue "Engine Models"'+str(name)+' Isp "'+str(isp)+'"')

	# Generates a ManeuverSummary to the filepath 
	## NOTE TO SELF - try to code without Execute Command and move to AstroSat
	def ManeuverSummary(self,name,filepath):
		self.root.ExecuteCommand('ReportCreate */Satellite/'+str(name)+' Type Save Style "Maneuver Summary" File "'+str(filepath)+'"')

	# Inserts the Solar System into the scenario
	def SolarSystem(self):
		self.Planet('Mercury')
		self.Planet('Venus')
		self.Planet('Earth')
		self.Planet('Mars')
		self.Planet('Jupiter')
		self.Planet('Saturn')
		self.Planet('Uranus')
		self.Planet('Neptune')
		self.Planet('Pluto')
		self.root.ExecuteCommand('Graphics */Planet/Mercury SetColor %105105105')
		self.root.ExecuteCommand('Graphics */Planet/Venus SetColor %123121000')
		self.root.ExecuteCommand('Graphics */Planet/Earth SetColor %014255198')
		self.root.ExecuteCommand('Graphics */Planet/Mars SetColor %255130014')
		self.root.ExecuteCommand('Graphics */Planet/Saturn SetColor %196000000')
		self.root.ExecuteCommand('Graphics */Planet/Jupiter SetColor %123000121')
		self.root.ExecuteCommand('Graphics */Planet/Neptune SetColor %123000000')
		self.root.ExecuteCommand('Graphics */Planet/Uranus SetColor %000123000')
		self.root.ExecuteCommand('Graphics */Planet/Pluto SetColor %000000123')

	def Radar(self,radarName,parentName,modelType):
		#modelType can be 'Monostatic', 'Bistatic Transmitter', 'Bistatic Receiver', 'Multifunction'
		from comtypes.gen import STKObjects
		from comtypes.gen import STKUtil
		parent = self.scenario.Children(str(parentName))
		radar = parent.Children.New(STKObjects.eRadar,str(radarName))
		radarInterface = radar.QueryInterface(STKObjects.IAgRadar)
		radarInterface.SetModel(str(modelType))
		return radarInterface

	def MonostaticRadar(self,radarName,parentName,modeType,antennaName):
		#modeType can be 'SAR', or 'Search Track'
		from comtypes.gen import STKObjects
		radar = self.Radar(str(radarName),str(parentName),'Monostatic')
		monostaticRadar = radar.Model.QueryInterface(STKObjects.IAgRadarModelMonostatic)
		monostaticRadar.SetMode(str(modeType))
		monostaticRadar.AntennaControl.ReferenceType = 0 #'eAntennaControlRefTypeLink'
		monostaticRadar.AntennaControl.LinkedAntennaObject = 'Antenna/'+str(antennaName)
		return monostaticRadar

	def MonostaticSAR(self,radarName,parentName,antennaName,pulseRepititionFrequency,rangeResolution,pulseCompressionRatio,numberOfPulses):
		from comtypes.gen import STKObjects
		SAR = self.MonostaticRadar(str(radarName),str(parentName),'SAR',str(antennaName))
		Pulse = SAR.Mode.QueryInterface(STKObjects.IAgRadarModeMonostaticSar).PulseDefinition
		Pulse.Prf = pulseRepititionFrequency
		Pulse.RangeResolution = rangeResolution
		Pulse.Pcr = pulseCompressionRatio
		Pulse.NumberOfPulses = numberOfPulses

	def MonostaticSearchTrack(self,radarName,parentName):
		from comtypes.gen import STKObjects
		SearchTrack = self.stk.MonostaticRadar(str(radarName),str(parentName),'Search Track',str(antennaName))

	def BistaticTxRadar(self,radarName,parentName):
		from comtypes.gen import STKObjects
		radar = self.Radar(str(radarName),str(parentName),'Bistatic Transmitter')

	def BistaticRxRadar(self,radarName,parentName):
		from comtypes.gen import STKObjects
		radar = self.Radar(str(radarName),str(parentName),'Bistatic Receiver')

	def MultifunctionRadar(self,radarName,parentName):
		from comtypes.gen import STKObjects
		radar = self.Radar(str(radarName),str(parentName),'Multifunction')

if __name__ == "__main__":
	from pySTK import *

	# Initialize Scenario
	stk = pySTK()
	stk.LoadScenario('C:\\Users\\jamie\\Desktop\\pySTK-Jupy\\MarsTerrainDefaultScenario\\MarsTerrainDefaultScenario.sc')
	startEpoch = '11 Oct 2024 00:00:00.000'
	stk.J2Sat('MarsSARSat','Mars',startEpoch,10,0.0002947,28.4,114,315,332)
	stk.Sensor('MarsSARSat','SARSensor')
	stk.DipoleAntenna('MarsSARSat','DipoleAntenna',20,60,2)
	stk.MonostaticSAR('SAR','MarsSARSat','DipoleAntenna',0.00070028,0.015,1000,20)
	#stk.SARSensor(self,parent,name,minElev,maxElev,foreExclusionAngle,parentAltitude)
	stk.SARSensor('MarsSARSat','SARSensor2',10,60,40,30,960)

	#stk.Scenario('test',startEpoch,'+1yr')

	# Solar System Scene & Planets
	#stk.InterplaneteryMode()
	#stk.SolarSystem()
	#stk.planetView('Mars')
	#stk.Place('VallesMarineris','Mars',-10,-72)
	#stk.Place('OlympusMons','Mars',18,-133)
	#stk.MarsTerrain()
	#stk.Asteroid('Bennu','C:\\Users\\jamie\\Desktop\\pySTK-Jupy\\bennu_results.txt',0.2625,6.14876955e-8)

	#stk.J2Sat('J2Sat2',startEpoch,15,0.0002947,28.4,114,315,332)
	#stk.Radar('radar1','J2Sat1','Bistatic Transmitter')
	#stk.MonostaticRadar('radar1','J2Sat1','SAR')
	#stk.MonostaticRadar('radar2','J2Sat2','Search Track')
	#stk.ParabolicAntenna('J2Sat1','ant1',7,30,65)
	#stk.DipoleAntenna('J2Sat1','dipole1',20,60,2)
	#stk.MonostaticSAR('radar1','J2Sat1','dipole1',0.00070028,0.015,1000,20)

	#stk.Terrain('Mars','C:\\Users\\jamie\\Downloads\\megr44s000hb.lbl')

	# Interplanetary Arc
	#stk.InterplanetaryLambertSolver('MarsArc','Sun','11 Oct 2024 12:00:00.00','216 Days','Earth','Mars','Heliocentric',6.9,4,'true','true')

	# Hohmann Transfer
	#stk.IspThrustEngine('engine1',550,350)

	# Delta V Budget
	#stk.ManeuverSummary('astroSat1','C:\\Users\\jamie\\Desktop\\mararcManeuverSummary.txt') #Insert your own filepath

	# Link Budget
	#stk.Facility('fac1',35.3376,-116.875,0.959634)
	#stk.ParabolicAntenna('fac1','ant1',7,30,65)
	#stk.ComplexRx('rx1','fac1',30,'ant1')
	#stk.ComplexTx('tx1','fac1',8.5,60,8,'ant1')

	#stk.ParabolicAntenna('astroSat1','ant2',7,3,65)
	#stk.ComplexRx('rx2','astroSat1',30,'ant2')
	#stk.ComplexTx('tx2','astroSat1',8.5,60,8,'ant2')

	#stk.planetView('Mars')
	#stk.planetView('Jupiter')
	#stk.planetView('Venus')
	#stk.planetView('Deimos')
	#stk.planetView('Asteroid1')
	#stk.planetView('Europa')

	# Test Functions
	#stk.AstroSatInsertSegment('astroSat2','Target_Sequence')
	#stk.AstroSatInsertManeuver('astroSat2','DV1','engine1')
	#stk.AstroSegmentsToString('astroSat2')
	#stk.AstroSatInsertPropagate('astroSat2','PropToOuterOrbit','Apoapsis')
	#stk.AstroSatInsertSegment('astroSat2','Propagate')

	#myScenario = stk.CurrentScenario()
	#root = stk.Root()
	#stk.TwoBodySat('twobodysat1')
	#stk.Satellite('sat1')