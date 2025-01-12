
export const districts = [
	"dolnośląskie",
	"kujawsko-pomorskie",
	"lubelskie",
	"lubuskie",
	"łódzkie",
	"małopolskie",
	"mazowieckie",
	"opolskie",
	"podkarpackie",
	"podlaskie",
	"pomorskie",
	"śląskie",
	"świętokrzyskie",
	"warmińsko-mazurskie",
	"wielkopolskie",
	"zachodniopomorskie",
];

// export const deliveryMethods = [
// 	'PICKUP',
// 	'TRUCK',
// 	'COURIER'
// ]

export const transportTypeText = {
	'PICKUP': 'Odbiór osobisty',
	'TRUCK': 'Ciężarówka',
	'COURIER': 'Kurier'
};

export const deliveryMethods = [...Object.keys(transportTypeText)];
