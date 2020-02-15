pragma solidity ^0.5.7;

contract Airbnb {

  // Property to be rented out on Airbnb
  struct Prescription {
    //string name;
    //string description;
    //bool isActive; // is property active
    //uint256 price; // per day price in wei (1 ether = 10^18 wei)
    //address owner; // Owner of the property
    // Is the property booked on a particular day,
    // For the sake of simplicity, we assign 0 to Jan 1, 1 to Jan 2 and so on
    // so isBooked[31] will denote whether the property is booked for Feb 1
    //bool[] isBooked;
        string patientHealthCardNumber;
	bool isFulfilled;
	uint256 price;
        string drugName;
        string frequency;
        string dosage;
        bool patientReceived;
	address owner;
  }

  uint256 public prescriptionId;

  // mapping of propertyId to Property object
  mapping(uint256 => Prescription) public prescriptions;

  // Details of a particular booking
  struct Payment {
    uint256 prescriptionId;
    uint256 DateBought;
    uint256 DateFulfilled;
    address user;
  }

  uint256 public paymentId;

  // mapping of bookingId to Booking object
  mapping(uint256 => Payment) public payments;

  // This event is emitted when a new property is put up for sale
  event NewPrescription (
    uint256 indexed prescriptionId
  );

  // This event is emitted when a NewBooking is made
  event NewPayment (
    uint256 indexed prescriptionId,
    uint256 indexed paymentId
  );

  /**
   * @dev Put up an Airbnb property in the market
   * @param name Name of the property
   * @param description Short description of your property
   * @param price Price per day in wei (1 ether = 10^18 wei)
   */
  function addPrescription(string memory patientHealthCardNumber, string memory drugName,string memory frequency,string memory dosage, uint256 price) public {
    Prescription memory prescription = Prescription(patientHealthCardNumber, false /* isActive */, price,drugName,frequency,dosage,false, msg.sender /* owner */);

    // Persist `property` object to the "permanent" storage
    prescriptions[prescriptionId] = prescription;

    // emit an event to notify the clients
    emit NewPrescription(prescriptionId++);
  }

  /**
   * @dev Make an Airbnb booking
   * @param _propertyId id of the property to rent out
   * @param checkInDate Check-in date
   * @param checkoutDate Check-out date
   */
  function buyPrescription(uint256 _prescriptionId, uint256 DateBought, uint256 DateFulfilled) public payable {
    // Retrieve `property` object from the storage
    Prescription storage prescription = prescriptions[_prescriptionId];

    // Assert that property is active
    require(
      prescription.isFulfilled == false,
      "property with this ID is not active"
    );


    // Check the customer has sent an amount equal to (pricePerDay * numberOfDays)
    require(
      msg.value == prescription.price,
      "Sent insufficient funds"
    );

    // send funds to the owner of the property
    _sendFunds(prescription.owner, msg.value);

    // conditions for a booking are satisfied, so make the booking
    _makePayment(_prescriptionId, DateBought, DateFulfilled);
  }

  function _makePayment(uint256 _prescriptionId, uint256 DateBought, uint256 DateFulfilled) internal {
    // Create a new booking object
    payments[paymentId] = Payment(_prescriptionId, DateBought, DateFulfilled, msg.sender);

    // Retrieve `property` object from the storage
    Prescription storage prescription = prescriptions[_prescriptionId];


    // Emit an event to notify clients
    emit NewPayment(_prescriptionId, paymentId++);
  }

  function _sendFunds (address beneficiary, uint256 value) internal {
    // address(uint160()) is a weird solidity quirk
    // Read more here: https://solidity.readthedocs.io/en/v0.5.10/050-breaking-changes.html?highlight=address%20payable#explicitness-requirements
    address(uint160(beneficiary)).transfer(value);
  }

  /**
   * @dev Take down the property from the market
   * @param _propertyId Property ID
   */
  function markPrescriptionAsFulfilled(uint256 _prescriptionId) public {

    prescriptions[_prescriptionId].isFulfilled = true;
  }
}
