import comtypes
from comtypes.gen import AgStkGatorLib
from comtypes.gen import STKObjects
from comtypes.gen import STKUtil

#insert - creates and adds to MCS main sequence and adds to component browser
#create - creates and adds to component browser

class AstroSat():

	def __init__(self,name,scenario,root):
		self.name = name
		self.scenario = scenario
		self.root = root
		self.satellite = self.root.CurrentScenario.Children.New(STKObjects.eSatellite,name)
		self.satInterface = self.satellite.QueryInterface(STKObjects.IAgSatellite)
		self.satInterface.SetPropagatorType(STKObjects.ePropagatorAstrogator)
		VOModel = self.satInterface.VO.Model
		VOModel.DetailThreshold.EnableDetailThreshold = False
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(name)+' DeleteSegment Propagate')
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(name)+' DeleteSegment "Initial State"')
		self.ASTG = self.satInterface.Propagator.QueryInterface(AgStkGatorLib.IAgVADriverMCS)
		self.MCS = self.ASTG.MainSequence

	def bplane(self):
		btemplate = self.satInterface.VO.BPlanes.Templates.Add()
		btemplate.Name = 'Lunar_B-Template'
		btemplate.CentralBody = 'Moon'
		btemplate.ReferenceVector = 'CentralBody/Moon Orbit_Normal Vector'
		binstance = self.satInterface.VO.BPlanes.Instances.Add(btemplate.Name)
		binstance.Name = 'LunarBPlane'

	def runMCS(self):
		self.ASTG.RunMCS()

	def runActiveProfile(self,targetSequenceName):
		self.MCS.Item(str(targetSequenceName)).Action = 'eVATargetSeqActionRunActiveProfiles'
		self.runMCS()

	def runActiveProfileOnce(self,targetSequenceName):
		self.MCS.Item(str(targetSequenceName)).Action = 'eVATargSeqRunActiveProfilesONCE'
		self.runMCS()

	def runActiveProfileSequence(self,sequenceName,targetSequenceName):
		targetSequence = self.MCS.Item(str(sequenceName)).QueryInterface(AgStkGatorLib.IAgVAMCSSequence).Segments.Item(str(targetSequenceName))
		targetInterface = targetSequence.QueryInterface(AgStkGatorLib.IAgVAMCSTargetSequence)
		targetInterface.Action = 1 #'eVATargetSeqActionRunActiveProfiles' 
		self.runMCS()

	def runActiveProfileSequenceOnce(self,sequenceName,targetSequenceName):
		targetSequence = self.MCS.Item(str(sequenceName)).QueryInterface(AgStkGatorLib.IAgVAMCSSequence).Segments.Item(str(targetSequenceName))
		targetInterface = targetSequence.QueryInterface(AgStkGatorLib.IAgVAMCSTargetSequence)
		targetInterface.Action = 2 #'eVATargetSeqActionRunActiveProfilesOnce'
		self.runMCS()

	def insertInitialStateKeplerian(self,segmentName,epoch,a,e,i,RAAN,w,TA):
		initialStateSegment = self.MCS.Insert(AgStkGatorLib.eVASegmentTypeInitialState,str(segmentName),'-')
		initialStateInterface = initialStateSegment.QueryInterface(AgStkGatorLib.IAgVAMCSInitialState)
		initialStateInterface.SetElementType(AgStkGatorLib.eVAElementTypeKeplerian)
		initialStateInterface.OrbitEpoch = str(epoch)
		keplerian = initialStateInterface.Element.QueryInterface(AgStkGatorLib.IAgVAElementKeplerian)
		keplerian.SemiMajorAxis = a
		keplerian.Eccentricity = e
		keplerian.Inclination = i
		keplerian.RAAN = RAAN
		keplerian.ArgOfPeriapsis = w
		keplerian.TrueAnomaly = TA

	def Launch(self,insertcreate,segmentName,segLocation,epoch):
		launchSegment = self.MCS.Insert(AgStkGatorLib.eVASegmentTypeLaunch,str(segmentName),str(segLocation))
		launchInterface = launchSegment.QueryInterface(AgStkGatorLib.IAgVAMCSLaunch)
		launchInterface.Epoch = epoch
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' AddToComponentBrowser MainSequence.SegmentList.'+str(segmentName))
		if insertcreate == 'create':
			self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' DeleteSegment '+str(segmentName))

	def PropagateDuration(self,insertcreate,segmentName,segLocation,triptime,propname):
		propagateSegment = self.MCS.Insert(AgStkGatorLib.eVASegmentTypePropagate,str(segmentName),str(segLocation))
		propagateInterface = propagateSegment.QueryInterface(AgStkGatorLib.IAgVAMCSPropagate)
		propagateInterface.PropagatorName = str(propname)
		stoppingConditionInterface = propagateInterface.StoppingConditions.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionCollection)
		stoppingConditionInterface2 = stoppingConditionInterface.Item(0).QueryInterface(AgStkGatorLib.IAgVAStoppingConditionElement)
		properties = stoppingConditionInterface2.Properties.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionComponent)
		properties2 = properties.QueryInterface(AgStkGatorLib.IAgVAStoppingCondition)
		properties2.Trip = triptime
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' AddToComponentBrowser MainSequence.SegmentList.'+str(segmentName))
		if insertcreate == 'create':
			self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' DeleteSegment '+str(segmentName))
		return propagateInterface

	def PropagatePeriapsis(self,insertcreate,segmentName,segLocation,centralbody,propname):
		propagateSegment = self.MCS.Insert(AgStkGatorLib.eVASegmentTypePropagate,str(segmentName),str(segLocation))
		propagateInterface = propagateSegment.QueryInterface(AgStkGatorLib.IAgVAMCSPropagate)
		propagateInterface.PropagatorName = str(propname)
		stoppingConditionInterface = propagateInterface.StoppingConditions.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionCollection)
		stoppingConditionInterface.Add('Periapsis')
		stoppingConditionInterface.Remove('Duration')
		stoppingConditionInterface2 = stoppingConditionInterface.Item(0).QueryInterface(AgStkGatorLib.IAgVAStoppingConditionElement)
		properties = stoppingConditionInterface2.Properties.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionComponent)
		properties2 = properties.QueryInterface(AgStkGatorLib.IAgVAStoppingCondition)
		properties2.CentralBodyName = centralbody
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' AddToComponentBrowser MainSequence.SegmentList.'+str(segmentName))
		if insertcreate == 'create':
			self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' DeleteSegment '+str(segmentName))
		return propagateInterface

	def removeSegment(self,segmentName):
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' DeleteSegment '+str(segmentName))

	def renameSegment(self,segmentName,segmentNewName):
		self.root.ExecuteCommand('Astrogator */Satellite/Satellite1 SetValue MainSequence.SegmentList'+str(segmentName)+'.ComponentName '+str(segmentNewName))

	def addAltitudeToPropagate(self,propagateInterface,segmentName,centralbody,trip):
		stoppingConditionInterface = propagateInterface.StoppingConditions.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionCollection)
		stoppingConditionInterface.Add('Altitude')
		stoppingConditionInterface2 = stoppingConditionInterface.Item(int(stoppingConditionInterface.Count) - 1).QueryInterface(AgStkGatorLib.IAgVAStoppingConditionElement)
		properties = stoppingConditionInterface2.Properties.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionComponent)
		properties2 = properties.QueryInterface(AgStkGatorLib.IAgVAStoppingCondition)
		properties2.Trip = trip
		properties2.CentralBodyName = str(centralbody)
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' AddToComponentBrowser MainSequence.SegmentList.'+str(segmentName))

	def addPeriapsisToPropagate(self,propagateInterface,segmentName,centralbody):
		stoppingConditionInterface = propagateInterface.StoppingConditions.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionCollection)
		stoppingConditionInterface.Add('Periapsis')
		stoppingConditionInterface2 = stoppingConditionInterface.Item(int(stoppingConditionInterface.Count) - 1).QueryInterface(AgStkGatorLib.IAgVAStoppingConditionElement)
		properties = stoppingConditionInterface2.Properties.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionComponent)
		properties2 = properties.QueryInterface(AgStkGatorLib.IAgVAStoppingCondition)
		properties2.CentralBodyName = str(centralbody)
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' AddToComponentBrowser MainSequence.SegmentList.'+str(segmentName))

	def PropagateAscendingNode(self,insertcreate,segmentName,segLocation,centralbody,propname):
		propagateSegment = self.MCS.Insert(AgStkGatorLib.eVASegmentTypePropagate,str(segmentName),str(segLocation))
		propagateInterface = propagateSegment.QueryInterface(AgStkGatorLib.IAgVAMCSPropagate)
		propagateInterface.PropagatorName = str(propname)
		stoppingConditionInterface = propagateInterface.StoppingConditions.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionCollection)
		stoppingConditionInterface.Add('AscendingNode')
		stoppingConditionInterface.Remove('Duration')
		stoppingConditionInterface2 = stoppingConditionInterface.Item(0).QueryInterface(AgStkGatorLib.IAgVAStoppingConditionElement)
		properties = stoppingConditionInterface2.Properties.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionComponent)
		properties2 = properties.QueryInterface(AgStkGatorLib.IAgVAStoppingCondition)
		properties2.CoordSystem = 'CentralBody/'+str(centralbody)+' Inertial'
		#properties2.CoordSystem(str(centralbody)+' Intertial')
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' AddToComponentBrowser MainSequence.SegmentList.'+str(segmentName))
		if insertcreate == 'create':
			self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' DeleteSegment '+str(segmentName))
		return propagateInterface

	def PropagateApoapsis(self,insertcreate,segmentName,segLocation,centralbody,propname):
		propagateSegment = self.MCS.Insert(AgStkGatorLib.eVASegmentTypePropagate,str(segmentName),str(segLocation))
		propagateInterface = propagateSegment.QueryInterface(AgStkGatorLib.IAgVAMCSPropagate)
		propagateInterface.PropagatorName = str(propname)
		stoppingConditionInterface = propagateInterface.StoppingConditions.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionCollection)
		stoppingConditionInterface.Add('Apoapsis')
		stoppingConditionInterface.Remove('Duration')
		stoppingConditionInterface2 = stoppingConditionInterface.Item(0).QueryInterface(AgStkGatorLib.IAgVAStoppingConditionElement)
		properties = stoppingConditionInterface2.Properties.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionComponent)
		properties2 = properties.QueryInterface(AgStkGatorLib.IAgVAStoppingCondition)
		properties2.CentralBodyName = centralbody
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' AddToComponentBrowser MainSequence.SegmentList.'+str(segmentName))
		if insertcreate == 'create':
			self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' DeleteSegment '+str(segmentName))
		return propagateInterface

	def PropagateRmag(self,insertcreate,segmentName,segLocation,centralbody,propname,trip):
		propagateSegment = self.MCS.Insert(AgStkGatorLib.eVASegmentTypePropagate,str(segmentName),str(segLocation))
		propagateInterface = propagateSegment.QueryInterface(AgStkGatorLib.IAgVAMCSPropagate)
		propagateInterface.PropagatorName = str(propname)
		stoppingConditionInterface = propagateInterface.StoppingConditions.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionCollection)
		stoppingConditionInterface.Add('R Magnitude')
		stoppingConditionInterface.Remove('Duration')
		stoppingConditionInterface2 = stoppingConditionInterface.Item(0).QueryInterface(AgStkGatorLib.IAgVAStoppingConditionElement)
		properties = stoppingConditionInterface2.Properties.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionComponent)
		properties2 = properties.QueryInterface(AgStkGatorLib.IAgVAStoppingCondition)
		properties2.Trip = trip
		if centralbody != 'Earth':
			properties2.ReferencePoint = str(centralbody)+' Center'
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' AddToComponentBrowser MainSequence.SegmentList.'+str(segmentName))
		if insertcreate == 'create':
			self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' DeleteSegment '+str(segmentName))
		return propagateInterface

	def Maneuver(self,insertcreate,segmentName,segLocation,manType,attitudeType,thrustaxes):
		maneuverSegment = self.MCS.Insert(AgStkGatorLib.eVASegmentTypeManeuver,str(segmentName),str(segLocation))
		maneuverInterface = maneuverSegment.QueryInterface(AgStkGatorLib.IAgVAMCSManeuver)
		if manType == 'Finite':
			manType = 1
		if manType == 'Impulsive':
			manType = 0
		if manType == 'Optimal Finite':
			manType = 2
		maneuverInterface.SetManeuverType(manType)
		if attitudeType == 'Along Velocity Vector':
			attitudeType = 0
		if attitudeType == 'AntiVelocity Vector':
			attitudeType = 1
		if attitudeType == 'Attitude':
			attitudeType = 2
		if attitudeType == 'File':
			attitudeType = 3
		if attitudeType == 'Thrust Vector':
			attitudeType = 4
		maneuverInterface.Maneuver.SetAttitudeControlType(attitudeType)
		ImpulsiveAttitudeControl = maneuverInterface.Maneuver.AttitudeControl.QueryInterface(AgStkGatorLib.IAgVAAttitudeControlImpulsive)
		ThrustVector = ImpulsiveAttitudeControl.QueryInterface(AgStkGatorLib.IAgVAAttitudeControlImpulsiveThrustVector)
		ThrustVector.ThrustAxesName = str(thrustaxes)
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' AddToComponentBrowser MainSequence.SegmentList.'+str(segmentName))
		if insertcreate == 'create':
			self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' DeleteSegment '+str(segmentName))
		return maneuverInterface

	def editManeuverThrust(self,maneuver,x,y,z):
		maneuverInterface = maneuver.QueryInterface(AgStkGatorLib.IAgVAMCSManeuver)
		ImpulsiveAttitudeControl = maneuverInterface.Maneuver.AttitudeControl.QueryInterface(AgStkGatorLib.IAgVAAttitudeControlImpulsive)
		ThrustVector = ImpulsiveAttitudeControl.QueryInterface(AgStkGatorLib.IAgVAAttitudeControlImpulsiveThrustVector)
		ThrustVector.AssignCartesian(x,y,z)

	def enableManeuverControl(self,seqName,manName,maneuverInterface,xyz):
		maneuverInterface = maneuverInterface.QueryInterface(AgStkGatorLib.IAgVAMCSManeuver)
		dc = self.differentialCorrector(seqName).QueryInterface(AgStkGatorLib.IAgVAProfileDifferentialCorrector)
		if xyz == 'x':
			maneuverInterface.EnableControlParameter(AgStkGatorLib.eVAControlManeuverImpulsiveCartesianX)
			xControlParam = dc.ControlParameters.GetControlByPaths(str(manName),"ImpulsiveMnvr.Cartesian.X")
			xControlParam.Enable = True
			xControlParam.MaxStep = 0.1
		if xyz == 'xy':
			maneuverInterface.EnableControlParameter(AgStkGatorLib.eVAControlManeuverImpulsiveCartesianX)
			maneuverInterface.EnableControlParameter(AgStkGatorLib.eVAControlManeuverImpulsiveCartesianY)
			xControlParam = dc.ControlParameters.GetControlByPaths(str(manName),"ImpulsiveMnvr.Cartesian.X")
			xControlParam.Enable = True
			xControlParam.MaxStep = 0.1
			yControlParam = dc.ControlParameters.GetControlByPaths(str(manName),"ImpulsiveMnvr.Cartesian.Y")
			yControlParam.Enable = True
			yControlParam.MaxStep = 0.1
		if xyz == 'xyz':
			maneuverInterface.EnableControlParameter(AgStkGatorLib.eVAControlManeuverImpulsiveCartesianX)
			maneuverInterface.EnableControlParameter(AgStkGatorLib.eVAControlManeuverImpulsiveCartesianY)
			maneuverInterface.EnableControlParameter(AgStkGatorLib.eVAControlManeuverImpulsiveCartesianZ)
			xControlParam = dc.ControlParameters.GetControlByPaths(str(manName),"ImpulsiveMnvr.Cartesian.X")
			xControlParam.Enable = True
			xControlParam.MaxStep = 0.1
			yControlParam = dc.ControlParameters.GetControlByPaths(str(manName),"ImpulsiveMnvr.Cartesian.Y")
			yControlParam.Enable = True
			yControlParam.MaxStep = 0.1
			zControlParam = dc.ControlParameters.GetControlByPaths(str(manName),"ImpulsiveMnvr.Cartesian.Z")
			zControlParam.Enable = True
			zControlParam.MaxStep = 0.1

	def enableLaunchEpoch(self,seqName,launchName,launchInterface):
		launchInterface = launchInterface.QueryInterface(AgStkGatorLib.IAgVAMCSLaunch)
		launchInterface.EnableControlParameter(AgStkGatorLib.eVAControlLaunchEpoch)
		dc = self.differentialCorrector(seqName).QueryInterface(AgStkGatorLib.IAgVAProfileDifferentialCorrector)
		launchParam = dc.ControlParameters.GetControlByPaths(str(launchName),'Launch.Epoch')
		launchParam.Enable = True

	def enableDurationControl(self,seqName,propName,propagateInterface):
		propagateInterface = propagateInterface.QueryInterface(AgStkGatorLib.IAgVAMCSPropagate)
		stoppingConditionInterface = propagateInterface.StoppingConditions.QueryInterface(AgStkGatorLib.IAgVAStoppingConditionCollection)
		stoppingConditionInterface2 = stoppingConditionInterface.Item(0).QueryInterface(AgStkGatorLib.IAgVAStoppingConditionElement)
		stoppingConditionInterface2.EnableControlParameter(AgStkGatorLib.eVAControlStoppingConditionTripValue)
		dc = self.differentialCorrector(seqName).QueryInterface(AgStkGatorLib.IAgVAProfileDifferentialCorrector)
		durationParam = dc.ControlParameters.GetControlByPaths(str(propName),'StoppingConditions.Duration.TripValue')
		durationParam.Enable = True

	def addManeuverInclinationResult(self,maneuverInterface,manName,seqName,centralBody,i):
		inclination = maneuverInterface.Results
		inclination.Add('Keplerian Elems/Inclination')
		dc = self.differentialCorrector(seqName).QueryInterface(AgStkGatorLib.IAgVAProfileDifferentialCorrector)
		inclinationResult = dc.Results.GetResultByPaths(str(manName),'Inclination')
		inclinationResult.Enable = True
		inclinationResult.DesiredValue = i
		inclinationResult.Tolerence = 0.1
		inclination.Item('Inclination').QueryInterface(AgStkGatorLib.IAgVAStateCalcInclination).CoordSystemName = 'CentralBody/'+str(centralBody)+' Inertial'

	def addManeuverEccentricityResult(self,maneuverInterface,manName,seqName,centralBody,e):
		eccentricity = maneuverInterface.Results
		eccentricity.Add('Keplerian Elems/Eccentricity')
		dc = self.differentialCorrector(seqName).QueryInterface(AgStkGatorLib.IAgVAProfileDifferentialCorrector)
		eccentricityResult = dc.Results.GetResultByPaths(str(manName),'Eccentricity')
		eccentricityResult.Enable = True
		eccentricityResult.DesiredValue = e
		eccentricityResult.Tolerence = 1
		eccentricity.Item('Eccentricity').QueryInterface(AgStkGatorLib.IAgVAStateCalcEccentricity).CentralBodyName = str(centralBody)

	def addApoapsisResult(self,maneuverInterface,manName,seqName,centralBody,r):
		apoapsis = maneuverInterface.Results
		apoapsis.Add('Keplerian Elems/Radius Of Apoapsis')
		dc = self.differentialCorrector(seqName).QueryInterface(AgStkGatorLib.IAgVAProfileDifferentialCorrector)
		apoapsisResult = dc.Results.GetResultByPaths(str(manName),'Radius_Of_Apoapsis')
		apoapsisResult.Enable = True
		apoapsisResult.DesiredValue = r
		apoapsisResult.Tolerence = 1
		if centralBody != 'Earth':
			apoapsis.Item('Apoapsis').QueryInterface(AgStkGatorLib.IAgVAStateCalcRadOfApoapsis).CentralBodyName = str(centralBody)

	def addDeltaDeclinationResult(self,segmentInterface,segName,seqName):
		deltaDeclination = segmentInterface.Results
		deltaDeclination.Add('MultiBody/Delta Declination')
		dc = self.differentialCorrector(seqName).QueryInterface(AgStkGatorLib.IAgVAProfileDifferentialCorrector)
		deltaDeclinationResult = dc.Results.GetResultByPaths(str(segName),'Delta_Declination')
		deltaDeclinationResult.Enable = True

	def addDeltaRightAscResult(self,segmentInterface,segName,seqName):
		deltaRightAsc = segmentInterface.Results
		deltaRightAsc.Add('MultiBody/Delta Right Asc')
		dc = self.differentialCorrector(seqName).QueryInterface(AgStkGatorLib.IAgVAProfileDifferentialCorrector)
		deltaRightAscResult = dc.Results.GetResultByPaths(str(segName),'Delta_Right_Asc')
		deltaRightAscResult.Enable = True

	def addBDotRResult(self,segmentInterface,segName,seqName,val):
		BDotR = segmentInterface.Results
		BDotR.Add('MultiBody/BDotR')
		dc = self.differentialCorrector(seqName).QueryInterface(AgStkGatorLib.IAgVAProfileDifferentialCorrector)
		BDotRResult = dc.Results.GetResultByPaths(str(segName),'BDotR')
		BDotRResult.Enable = True
		BDotRResult.DesiredValue = val

	def addBDotTResult(self,segmentInterface,segName,seqName,val):
		BDotT = segmentInterface.Results
		BDotT.Add('MultiBody/BDotT')
		dc = self.differentialCorrector(seqName).QueryInterface(AgStkGatorLib.IAgVAProfileDifferentialCorrector)
		BDotTResult = dc.Results.GetResultByPaths(str(segName),'BDotT')
		BDotTResult.Enable = True
		BDotTResult.DesiredValue = val

	def differentialCorrector(self,seqName):
		dc = seqName.Profiles.Item('Differential Corrector')
		return dc

	def insertTargetSequence(self,segmentName,segLocation):
		targetSegment = self.MCS.Insert(AgStkGatorLib.eVASegmentTypeTargetSequence,str(segmentName),str(segLocation))
		targetInterface = targetSegment.QueryInterface(AgStkGatorLib.IAgVAMCSTargetSequence)
		self.root.ExecuteCommand('Astrogator */Satellite/'+str(self.name)+' AddToComponentBrowser MainSequence.SegmentList.'+str(segmentName))
		targetInterface.Action = 1	#eVATargetSeqActionRunActiveProfiles
		return targetInterface 		#returns pointer to TargetSequence

	def insertSegmentToSequenceByName(self,seqName,segmentName):
		currentsegment = seqName.Segments.InsertByName(str(segmentName),'-')
		return currentsegment

	def insertSegmentByName(self,segmentName):
		currentsegment = self.MCS.InsertByName(str(segmentName),'-')
		return currentsegment

	def createAndAddToSequence(self,seqName,segmenttype,segmentName):
		self.createSegmentComponent(str(segmenttype),str(segmentName))
		seqName.Segments.InsertByName(str(segmentName),'-')

	def createSegmentComponent(self,segmenttype,segmentName):
		ComponentCollection = self.scenario.ComponentDirectory.GetComponents(STKObjects.eComponentAstrogator)
		MCSComponents = ComponentCollection.GetFolder('MCS Segments')
		MCSComponents.DuplicateComponent(str(segmenttype),str(segmentName))

if __name__ == "__main__":
	from pySTK import *
	from AstroSat import *

	# Initialize Scenario
	stk = pySTK()
	root = stk.Root()
	startEpoch = '11 Oct 2024 00:00:00.000'
	test = stk.Scenario('test',startEpoch,'+1yr')
	stk.InterplaneteryMode()
	stk.planetView('Mars')

	stk.Planet('Mars')
	sat = AstroSat('sat1',test,root)

	stk.InterplanetaryLambertSolver('MarsArc','Sun',
                                startEpoch,
                                '216 Days','Earth','Mars',
                                'Heliocentric',6.9,4,
                                'true','true')
	sat.insertSegmentByName('MarsArc')
	sat.PropagateAscendingNode('insert','prop2ascendingnode','-','Mars','MarsPointMass')
	sat.runActiveProfileSequence('MarsArc','Target Sequence')
	sat.runActiveProfileSequenceOnce('MarsArc','Target Sequence')

	#sat.insertInitialStateKeplerian('InnerOrbit','11 Oct 2024 00:00:000.00',7500,0.1,45,0,0,0)

	#sat.PropagateDuration('insert','1day','-',86400,'MarsPointMass')
	#sat.PropagateDuration('create','2day','-',86400*2,'MarsPointMass')
	#PropToPeri = sat.PropagatePeriapsis('insert','PropToPeri','-','Mars','MarsPointMass')
	#sat.addAltitudeToPropagate(PropToPeri,'Earth',0)
	#sat.PropagatePeriapsis('create','PropToPeriapsis','-','Mars','MarsPointMass')

	#sat.PropagateApoapsis('insert','PropToApoapsis','-','Jupiter','JupiterPointMass')

	#HohmannTransfer = sat.insertTargetSequence('HohmannTransfer','-')

	#DV2 = sat.Maneuver('create','DV2','-','Impulsive','Thrust Vector','Satellite VNC(Earth)')
	
	#DV2 = sat.insertSegmentToSequenceByName(HohmannTransfer,'DV2')
	#sat.editManeuverThrust(DV2,3100,0,0)
	#sat.enableManeuverControl(HohmannTransfer,'DV2',DV2,'xyz')
	#sat.insertSegmentToSequenceByName(HohmannTransfer,'PropToPeriapsis')
	#sat.insertSegmentToSequenceByName(HohmannTransfer,'2day')

	#sat.addManeuverInclinationResult(DV2,'DV2',HohmannTransfer,'Mars',20)
	#sat.addManeuverEccentricityResult(DV2,'DV2',HohmannTransfer,'Mars',0.01)
	#sat.differentialCorrector(HohmannTransfer)

	#sat.runActiveProfile('HohmannTransfer')
	#sat.runActiveProfileOnce('HohmannTransfer')

	#sat.Launch('create','launch','-','11 Oct 2024 00:00:000.00')
	#sat.PropagateRmag('insert','RMAG','-','Earth','CisLunar',30000)

	#sat.insertSegmentByName('PropToPeri')


	#sat.insertPropagatePeriapsis('PropToPeriapsis','-','Mars','MarsPointMass')
	#sat.Maneuver('insert','DV1','-','Impulsive','Thrust Vector','Satellite VNC(Earth)')
	#sat.createAndAddToSequence(HohmannTransfer,'Maneuver','DV2')
	#sat.insertPropagateDuration('1day','-',86400,'Earth HPOP Default v10')
	#sat.createPropagateDuration('2day','-',86400*2,'MarsPointMass')
	#sat.enableManeuverControl(DV2,'x')
	#sat.createSegmentComponent('Propagate','PropToPeriapsis')
	#sat.insertPropagateApoapsis('ProptoApoapsis2','HohmannTransfer','Earth','Earth HPOP Default v10')
	#sat.insertManeuver('DV2','Optimal Finite')