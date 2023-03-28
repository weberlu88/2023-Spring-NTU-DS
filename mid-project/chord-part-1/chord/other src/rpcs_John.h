#ifndef RPCS_H
#define RPCS_H

#include "chord.h"
#include "rpc/client.h"

#include <iostream>
#include <cstdint>
#include <vector>

Node self, successor, predecessor;
Node finger_table[4]; // len = 4
std::vector<Node> successor_list(3); // len = 3

Node get_info() { return self; } // Do not modify this line.
Node get_predecessor() { return predecessor; }
Node get_successor() { return successor; } // use by python test code
std::vector<Node> get_successor_list() { return successor_list; }

void create() {
  predecessor.ip = "";
  successor = self;
  successor_list[0] = self;
}

void change_predecessor(Node n) {
  predecessor = n;
}

// no use
void change_successor(Node n) {
  successor = n;
}

void join(Node n) { // n is a known node on Chrod ring
  predecessor.ip = "";

  try {
    rpc::client client(n.ip, n.port); // get the known node instance
    successor = client.call("find_successor", self.id).as<Node>(); // use the known node to find the successor by new node id
    
    std::vector<Node> new_successor_list = client.call("get_successor_list").as<std::vector<Node>>();

    successor_list[0] = successor;
    successor_list[1] = new_successor_list[0];
    successor_list[2] = new_successor_list[1];

    // std::cout << "Node:" << self.id << "\n";
    // std::cout << "     Su list 0:" << successor_list[0].id  << "\n";
    // std::cout << "     Su list 1:" << successor_list[1].id  << "\n";
    // std::cout << "     Su list 2:" << successor_list[2].id  << "\n";

  } catch (std::exception &e) {
    // std::cout << "join err" << "\n";
  }

}

bool isBetween_inclusive(uint64_t id, uint64_t predecessor_id, uint64_t successor_id){
  if (successor_id > predecessor_id) {
    if (id > predecessor_id && id <= successor_id) {
      return true;
    } else {
      return false;
    }
  } else { // successor_id <= predecessor_id
    if ( id > predecessor_id || id <= successor_id) {
      return true;
    } else {
      return false;
    }
  }
}

bool isBetween(uint64_t id, uint64_t predecessor_id, uint64_t successor_id){
  if (successor_id > predecessor_id) {
    if (id > predecessor_id && id < successor_id) {
      return true;
    } else {
      return false;
    }
  } else { // successor_id <= predecessor_id
    if ( id > predecessor_id || id < successor_id) {
      return true;
    } else {
      return false;
    }
  }
}

uint64_t add_id(uint64_t id_1, uint64_t id_2) {
  return (id_1 + id_2) & ((1UL << 32) - 1);
}

Node closest_preceding_node (uint64_t id) {
  for ( int i = 3; i >= 0; i-- ) {
    
    // if (self.id == 373792412 && id == 100663296) {
    //   std::cout << "ID:" << id << "\n";
    //   std::cout << "Finger id:" << finger_table[i].id << "\n";
    //   std::cout << "Self id:" << self.id << "\n";
    // }    

    if ( isBetween(finger_table[i].id, self.id, id) ) {
      if (finger_table[i].id != 0 && finger_table[i].id != self.id){

        return finger_table[i];
      } 
    }
  }

  return self;
}

/* finger table version */
Node find_successor(uint64_t id) {
  // TODO: implement your `find_successor` RPC
  Node closest_node;
  try {

    if ( isBetween_inclusive(id, self.id, successor.id) ){
      // std::cout << "Node:" << self.id << ": Direct Return \n";

      return successor;

    } else {
 
      closest_node = closest_preceding_node(id);
      if (closest_node.id == self.id) {

        return self;
      } else {
        rpc::client client(closest_node.ip, closest_node.port); 
        return client.call("find_successor", id).as<Node>();
      }
    }

  } catch (std::exception &e) {
    // Handling Fail
    // std::cout << "Node:" << self.id << ":find_successor err" << "\n" ;
    // std::cout << "     Close Node:" << closest_node.id << "\n" ;


  }
  return self;
}

uint64_t next = 0;
void fix_fingers(){
  try {
    if (next >= 4){
      next = 0;
    }

    if (next != 0){
      finger_table[next] = find_successor( add_id(self.id, (1ULL << (28+next)) ) );
    } else {
      finger_table[next] = successor;
    }

    // std::cout << "Node:" << self.id << "\n";
    // std::cout << "        Finger " << next << " ID:" << add_id(self.id, (1ULL << (28+next)) ) << "\n";
    // std::cout << "        Finger " << next << " Node:" << finger_table[next].id << "\n";
    
    next = next + 1;
  } catch (std::exception &e) {
    // std::cout << "fix_fingers err" << "\n" ;
  } 
}

void update_finger_table(Node died_node, Node new_node){
  for (int i=0; i<=3; i++){
    if (died_node.id == finger_table[i].id) {
      finger_table[i] = new_node;
    }
  }
}

void update_successor_list(Node su_node) {
  successor_list[0] = su_node;

  rpc::client client(successor.ip, successor.port); 
  std::vector<Node> new_successor_list = client.call("get_successor_list").as<std::vector<Node>>();

  successor_list[1] = new_successor_list[0];
  successor_list[2] = new_successor_list[1];

}

void stablize(){

  try {

    Node candidate_s;

    if ( successor.id != 0 && self.id != successor.id ) {

      rpc::client client(successor.ip, successor.port); 
      // try 1: test successor is alive or not
      // try 2: test successor.predecessor is alive or not
      candidate_s = client.call("get_predecessor").as<Node>();

    } else { // when only have root node [self.id == successor.id]
      candidate_s = predecessor;
      // std::cout << "IN sta:" << candidate_s.id << "\n";
    }

    if (candidate_s.id != 0) { // check if candidate_s exist. if exist, check weather to change the successor
      if ( isBetween(candidate_s.id, self.id, successor.id) ) {
        successor = candidate_s;
      } 
    } 
    
    if ( successor.id != 0 && self.id != successor.id) {
      // if (temp_su_id != successor.id) { // if successor change, tell it to change predecessor

      // std::cout << "Node:" << self.id << " Port: " << self.port << "\n";
      // std::cout << "    Out Self id:" << self.id << " Successor id: " << successor.id << "\n";
      rpc::client client2(successor.ip, successor.port);

      // std::cout << "Notify Node  :" << successor.port << "\n";
      client2.call("notify", self);   

      update_successor_list(successor);
      // }
    }
  } catch (std::exception &e) {

    // std::cout << "stablize Err \n";
    // case: successor died, fail to find the successor.predecessor
    // let successor_list[1] as alternative successor, replace the origin one
    if (successor.id == successor_list[0].id) { 
      // std::cout << "Node:" << self.id << " Port: " << self.port << "\n";
      // std::cout << "    stablize Err" << ":successor.id == successor_list[0].id" << "\n";

      try {

        if (successor_list[1].id != self.id) {
          rpc::client client3(successor_list[1].ip, successor_list[1].port);
          std::vector<Node> new_successor_list = client3.call("get_successor_list").as<std::vector<Node>>();

          // std::cout << "Node:" << self.id << " Port: " << self.port << "\n";
          // std::cout << "    stablize Err" << ":catch 1 successor port:" << successor_list[1].port << "\n";
          
          /*update successor, successor_list, finger_table*/
          update_finger_table(successor_list[0], successor_list[1]);
          
          successor = successor_list[1];
          successor_list[0] = successor_list[1];
          successor_list[1] = new_successor_list[0];
          successor_list[2] = new_successor_list[1];

          // std::cout << "Node:" << self.id << " Port: " << self.port << "\n";
          // std::cout << "    Self id:" << self.id << " Successor id: " << successor.id << "\n";
        } else { // successor == self, so only exit one node


          finger_table[0] = self;
          finger_table[1] = self;
          finger_table[2] = self;
          finger_table[3] = self;

          successor = self;
          Node temp_node{};
          predecessor = temp_node;
          successor_list[0] = self;
          successor_list[1] = self;
          successor_list[2] = self;

          // std::cout << "Node:" << self.id << " Port: " << self.port << "\n";
          // std::cout << "    In Self id:" << self.id << " Successor id: " << successor.id << "\n";
        }
        


      } catch (std::exception &e) {
        // std::cout << "Node:" << self.id << " Port:" << self.port << "\n";
        // std::cout << "    stablize Err" << "catch 1 fail successor port: " <<  successor_list[1].port <<  "\n";
        try {
          if (successor_list[1].id != self.id) {
            rpc::client client4(successor_list[2].ip, successor_list[2].port);
            std::vector<Node> new_successor_list = client4.call("get_successor_list").as<std::vector<Node>>();
            
            update_finger_table(successor_list[0], successor_list[2]);
            update_finger_table(successor_list[1], successor_list[2]);

            successor = successor_list[2];
            successor_list[0] =  successor_list[2];
            successor_list[1] = new_successor_list[0];
            successor_list[2] = new_successor_list[1];          
          } else { // successor == self, so only exit one node
            finger_table[0] = self;
            finger_table[1] = self;
            finger_table[2] = self;
            finger_table[3] = self;

            successor = self;
            Node temp_node{};
            predecessor = temp_node;
            successor_list[0] = self;
            successor_list[1] = self;
            successor_list[2] = self;
          }


        } catch (std::exception &e) {
          // std::cout << "Node:" << self.id << " Port:" << self.port << "\n";
          // std::cout << "    stablize Err" << "catch 2 fail successor port: " <<  successor_list[2].port <<  "\n";
          // std::cout << "Three node die in a row" << "\n";
        }
      }

    } else { // after changing the successor to successor.predecessor, successor.predecessor is died
      
      // because successor.predecessor is died, we no need to change successor, but need to restore successor
      successor = successor_list[0];
      Node temp_node{};

      rpc::client client5(successor.ip, successor.port);
      client5.call("change_predecessor", temp_node); // tell the successor its predecessor is died
      // std::cout << "Node:" << self.id << " Port:" << self.port << "\n";
      // std::cout << "    stablize Err" << ":no notify to change successor" << "\n";
    }


  }

}

void notify(Node n){
  // std::cout << "In notify  :" << self.port << "\n";
  // std::cout << "In notify  :" << predecessor.ip << "\n";

  if ( predecessor.ip == "" || isBetween(n.id, predecessor.id, self.id) ) {
    predecessor = n;
    // std::cout << "notify()" << "\n" ;
  }

}

void check_predecessor() {
  try {
    rpc::client client(predecessor.ip, predecessor.port);
    Node n = client.call("get_info").as<Node>();
  } catch (std::exception &e) {
    predecessor.ip = "";
    // std::cout << "check_predecessor Err \n";
  }
}

void register_rpcs() {
  add_rpc("get_info", &get_info); // Do not modify this line.
  add_rpc("get_predecessor", &get_predecessor); 
  add_rpc("change_predecessor", &change_predecessor);
  add_rpc("notify", &notify);
  add_rpc("get_successor_list", &get_successor_list);
  add_rpc("create", &create);
  add_rpc("join", &join);
  add_rpc("find_successor", &find_successor);
}

void register_periodics() {
  add_periodic(check_predecessor);
  add_periodic(stablize);
  add_periodic(fix_fingers);
}

#endif /* RPCS_H */
