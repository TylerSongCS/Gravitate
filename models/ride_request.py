"""Author: Zixuan Rao, Andrew Kim
"""


from google.cloud.firestore import DocumentReference, Transaction
from models.target import Target, ToEventTarget, FromEventTarget
from data_access.ride_request_dao import RideRequestGenericDao

class RideRequest(object):

    __firestoreRef: DocumentReference = None

    """ Description	
        This class represents a RideRequest object
    
    """

    def setFirestoreRef(self, firestoreRef):
        self.__firestoreRef = firestoreRef

    def getFirestoreRef(self):
        """
            TODO refer to https://stackoverflow.com/questions/50012956/firestore-how-to-store-reference-to-document-how-to-retrieve-it
            :param self: 
        """   
        return self.__firestoreRef
    
    @staticmethod
    def fromDictAndReference(rideRequestDict, rideRequestRef):
        rideRequest = RideRequest.fromDict(rideRequestDict)
        rideRequest.setFirestoreRef(rideRequestRef)
        return rideRequest

    @staticmethod
    def fromDict(rideRequestDict):
        """ Description
            This function creates AirportRideRequest or SocialEventRideRequest. 
                (RideRequest Factory)

            :param rideRequestDict: 
        """
        rideRequestType = rideRequestDict['rideCategory']

        driverStatus = rideRequestDict['driverStatus']
        pickupAddress = rideRequestDict['pickupAddress']
        hasCheckedIn = rideRequestDict['hasCheckedIn']
        eventRef = rideRequestDict['eventRef'] # TODO conversion to DocumentReference
        orbitRef = rideRequestDict['orbitRef']
        target = Target.fromDict(rideRequestDict['target'])
        pricing = rideRequestDict['pricing']

        if rideRequestType == 'airportRide':
            flightLocalTime = rideRequestDict['flightLocalTime']
            flightNumber = rideRequestDict['flightNumber']
            airportLocation = rideRequestDict['airportLocation']
            baggages = rideRequestDict['baggages']
            disabilities = rideRequestDict['disabilities']

            return AirportRideRequest(driverStatus, pickupAddress, hasCheckedIn,
                                      eventRef, orbitRef, target, pricing, flightLocalTime, 
                                      flightNumber, airportLocation, baggages, disabilities)
        elif rideRequestType == 'eventRide':
            # TODO change function calls
            return SocialEventRideRequest(driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target, pricing)
        else:
            raise Exception(
                'Not supported rideRequestType: {}'.format(rideRequestType))

    def toDict(self):
        rideRequestDict = {
            'driverStatus': self.driverStatus,
            'pickupAddress': self.pickupAddress,
            'hasCheckedIn': self.hasCheckedIn,
            'eventRef': self.eventRef,
            'orbitRef': self.orbitRef,
            'target': self.target.toDict(),
            'pricing': self.pricing
        }
        return rideRequestDict

    def save(self, transaction: Transaction = None):
        if (self.getFirestoreRef()):
            if not transaction:
                raise Exception('transaction is not provided. ')
            RideRequestGenericDao().setRideRequestWithTransaction(transaction, self, self.getFirestoreRef())
        else:
            newRef = RideRequestGenericDao().createRideRequest(self)
            self.setFirestoreRef(newRef)


    def __init__(self, driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target, pricing):
        """ Description
            This function initializes a RideRequest Object. 
            Note that this function should not be called directly. 

            :param self: 
            :param driverStatus: 
            :param pickupAddress: 
            :param hasCheckedIn: 
            :param eventRef: 
            :param orbitRef: 
            :param target: 
            :param pricing: 
        """

        self.driverStatus = driverStatus
        self.pickupAddress = pickupAddress
        self.hasCheckedIn = hasCheckedIn
        self.eventRef = eventRef
        self.orbitRef = orbitRef
        self.target = target
        self.pricing = pricing


# class RideRequestActiveRecord(RideRequest):
    
#     @staticmethod
#     def fromFirestoreRef(firestoreRef, rideRequestDAO: RideRequestGenericDao, transaction: Transaction = None):
#         if (transaction):
#             return rideRequestDAO.getRideRequestWithTransaction(transaction, firestoreRef)
#         else:
#             return rideRequestDAO.getRideRequest(firestoreRef)

#     @staticmethod
#     def createFromDict(rideRequestDict, rideRequestGenericDao = RideRequestGenericDao()):
#         rideRequest = RideRequest.fromDict(rideRequestDict)
#         timestamp, documentRef = rideRequestGenericDao.createRideRequest()
#         rideRequest.setFirestoreRef(documentRef)
#         return rideRequest
    
#     def saveWithTransaction(self, transaction: Transaction):
#         # Save to database with ref specified instance variable
#         if (not self.__firestoreRef):
#             raise Exception('self.__firestoreRef not defined!')
#         RideRequestGenericDao.setRideRequestWithTransaction(transaction, self, self.__firestoreRef)
 

class AirportRideRequest(RideRequest):

    # TODO more arguments
    def __init__(self, driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target, pricing, flightLocalTime, flightNumber, airportLocation, baggages, disabilities):
        """ Description
            Initializes an AirportRideRequest Object 
            Note that this class should not be initialzed directly.
            Use RideRequest.fromDict to create an AirportRideRequest.

            :param self: 
            :param driverStatus: 
            :param pickupAddress: 
            :param hasCheckedIn: 
            :param eventRef: 
            :param orbitRef: 
            :param target: 
            :param pricing: 
            :param flightLocalTime: 
            :param flightNumber: 
            :param airportLocation: 
            :param baggages: 
            :param disabilities: 
        """

        super().__init__(driverStatus, pickupAddress,
                         hasCheckedIn, eventRef, orbitRef, target, pricing)
        self.rideCategory = 'airportRide'
        self.flightLocalTime = flightLocalTime
        self.flightNumber = flightNumber
        self.airportLocation = airportLocation
        self.baggages = baggages
        self.disabilities = disabilities

    def toDict(self):
        """ Description
            This function returns the dictionary representation of a RideRequest object 
                so that it can be stored in the database. 

        :type self:
        :param self:

        :raises:

        :rtype:
        """

        rideRequestDict = super().toDict()

        rideRequestDict['rideCategory'] = 'airportRide'
        rideRequestDict['flightLocalTime'] = self.flightLocalTime
        rideRequestDict['flightNumber'] = self.flightNumber
        rideRequestDict['airportLocation'] = self.airportLocation
        rideRequestDict['baggages'] = self.baggages
        rideRequestDict['disabilities'] = self.disabilities
        return rideRequestDict


class SocialEventRideRequest(RideRequest):

    # TODO more arguments
    def __init__(self, driverStatus, pickupAddress, hasCheckedIn, eventRef, orbitRef, target, pricing):
        """ Description
            Initializes a SocialEventRideRequest Object
            Note that this class should not be initialzed directly.
            Use RideRequest.fromDict to create a SocialEventRideRequest.

        :type self:
        :param self:

        :type dictionary:
        :param dictionary:

        :raises:

        :rtype:
        """

        super().__init__(driverStatus, pickupAddress,
                         hasCheckedIn, eventRef, orbitRef, target, pricing)
        self.rideCategory = 'eventRide'

    def toDict(self):
        rideRequestDict = super().toDict()
        rideRequestDict['rideCategory'] = 'eventRide'
        return rideRequestDict
