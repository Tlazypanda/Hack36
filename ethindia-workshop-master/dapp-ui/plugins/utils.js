import AirbnbABI from './airbnbABI'
const Web3 = require('web3')

let metamaskWeb3 = new Web3('http://localhost:8545')
let account = null
let airbnbContract
let airbnbContractAddress = '' // Paste Contract address here

export function web3() {
  return metamaskWeb3
}

export const accountAddress = () => {
  return account
}

export async function setProvider() {
if (window.ethereum) {
    metamaskWeb3 = new Web3(ethereum);
    try {
      // Request account access if needed
      await ethereum.enable();
    } catch (error) {
      // User denied account access...
    }
  }
  else if (window.web3) {
    metamaskWeb3 = new Web3(web3.currentProvider);
  }
  account = await metamaskWeb3.eth.getAccounts()
  // TODO: get injected Metamask Object and create Web3 instance

}


function getAirbnbContract() {
  airbnbContract = airbnbContract || new metamaskWeb3.eth.Contract(AirbnbABI.abi, airbnbContractAddress)
  return airbnbContract
}


export async function postProperty(healthCardNumber, drugName, frequency,dosage,price) {
 const prop = await getAirbnbContract().methods.addPrescription(healthCardNumber, drugName, frequency,dosage,price).send({
    from: account[0]
  })
  alert('Prescription Posted Successfully')
}

export async function bookProperty(prescriptionId,DateBought,DateFulfilled,totalPrice) {
 const prop = await getAirbnbContract().methods.buyPrescription(prescriptionId,DateBought,DateFulfilled).send({
    from: account[0],
    value: totalPrice, //for testing
  })
  alert('Prescription ordered Successfully')
}

export async function fetchAllProperties() {
  // TODO: call Airbnb.propertyId
  // iterate till property Id
  // push each object to properties array
 const propertyId = await getAirbnbContract().methods.prescriptionId().call()
  // iterate till property Id
  const prescriptions = []
  for (let i = 0; i < propertyId; i++) {
    const p = await airbnbContract.methods.prescriptions(i).call()
    prescriptions.push({
      id: i,
      healthCardNumber: p.healthCardNumber,
      drugName: p.drugName,
      price: metamaskWeb3.utils.fromWei(p.price),
      frequency: p.frequency,
      dosage: p.dosage
    })
  }
  return prescriptions
}
